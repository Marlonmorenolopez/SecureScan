"""
SecureScan Pro v5.0 - Backend API
Flask application with Redis for persistent storage

CORRECCIONES ACUMULADAS v5.0:
  1.  Race condition en run_scan() — resultados se persisten en Redis
      inmediatamente tras cada herramienta; el guardado final usa una
      copia fresca leída de Redis, no la variable local inicial.
  2.  CORS lee orígenes desde variable de entorno ALLOWED_ORIGINS.
  3.  get_scan_storage() cachea el estado de conexión (10s) para evitar
      ping a Redis en cada operación.
  4.  scans_fallback usa threading.Lock para acceso seguro multi-hilo.
  5.  FORBIDDEN_PATTERNS: eliminada excepción inconsistente en 10.x.x.x.
  6.  request.get_json() usa silent=True — sin crash con body malformado.
  7.  app.secret_key asignada desde SECRET_KEY con validación.
  8.  Autenticación por token (X-API-Token) en endpoints sensibles.
  9.  Rate limiting con flask-limiter para evitar abuso.
  10. Validación de scan_id como UUID v4 antes de cada operación.
  11. RESTRICT_TO_LAB_TARGETS leída desde variable de entorno.
  12. ZAP unificado en un solo paso usando run_zap_full() — elimina
      doble ejecución y el bug de Spider ID inválido (0).
  13. Numeración de pasos corregida en run_scan() (sin duplicados).
  14. Patator en Paso 3 — antes de Nuclei (Paso 8) para que la cookie
      esté disponible para todas las herramientas.
  15. Comentario incorrecto sobre tuplas de 2 corregido — son de 3
      (url, params, data).
  16. scans_fallback limitado a 200 entradas para evitar OOM sin Redis.
  17. Thread de escaneo daemon=False para sobrevivir al worker de gunicorn.
  18. Paso 9 integra run_injection_scan() (10 técnicas) con fallback
      a SQLMap si InjectionScanner no está instalado.
  19. inject_urls protegido con hasattr() en el paso de ZAP.
  20. Nombre de campo corregido: nuclei_findings (antes nikto_findings).
"""

import os
import re
import json
import socket
import uuid
import uuid as uuid_module
import time
import logging
import threading
import ipaddress
from datetime import datetime
from functools import wraps
from typing import Dict, List, Optional
from urllib.parse import urlparse
from utils.i18n_backend import get_t, locale_from_request

def _t(key: str, **kwargs) -> str:
    """Shorthand: traduce key al locale de la request actual."""
    return get_t(locale_from_request(request))(key, **kwargs)

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis

try:
    from modules.orchestrator import SecurityOrchestrator
except ImportError as e:
    print(f"DEBUG: Error importando directamente: {e}")
    import importlib.util
    import sys
    spec   = importlib.util.spec_from_file_location("orchestrator", "/app/modules/orchestrator.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    SecurityOrchestrator = module.SecurityOrchestrator
    print("DEBUG: SecurityOrchestrator cargado vía fallback manual")

from utils.scoring  import calculate_security_score
from utils.reporter import generate_report

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# ── Flask app ─────────────────────────────────────────────────────────────────
app = Flask(__name__)

_secret_key = os.environ.get('SECRET_KEY', '')
if not _secret_key or 'CAMBIA' in _secret_key or 'change' in _secret_key.lower():
    if os.environ.get('FLASK_ENV') != 'development':
        raise RuntimeError(
            "SECRET_KEY debe ser una clave segura en producción. "
            "Genera una con: openssl rand -hex 32"
        )
    _secret_key = 'dev-only-insecure-key'
    logger.warning("Usando SECRET_KEY de desarrollo — NO usar en producción.")
app.secret_key = _secret_key

_allowed_origins = os.environ.get(
    'ALLOWED_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000',
).split(',')
CORS(app, origins=[o.strip() for o in _allowed_origins])

# ── Redis ─────────────────────────────────────────────────────────────────────
redis_url    = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
redis_client = redis.from_url(redis_url, decode_responses=True)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri=redis_url,
    default_limits=["500 per day", "100 per hour"],
)

# ── Configuración ─────────────────────────────────────────────────────────────
ZAP_API_KEY  = os.environ.get('ZAP_API_KEY',  'securescan-dev-key-2024')
ZAP_API_URL  = os.environ.get('ZAP_API_URL',  'http://localhost:8080')
MSF_HOST     = os.environ.get('MSF_HOST',     '127.0.0.1')
MSF_PORT     = int(os.environ.get('MSF_PORT', '55553'))
MSF_PASSWORD = os.environ.get('MSF_PASSWORD', 'msf')

API_TOKEN = os.environ.get('API_TOKEN', '')
if not API_TOKEN:
    logger.warning(
        "API_TOKEN no configurado — todos los endpoints son accesibles sin autenticación. "
        "Configura API_TOKEN en .env para entornos expuestos."
    )

ALLOWED_LAB_TARGETS = os.environ.get(
    'ALLOWED_LAB_TARGETS',
    'juice-shop:3000,dvwa:80,webgoat:8080',
).split(',')

RESTRICT_TO_LAB = os.environ.get('RESTRICT_TO_LAB_TARGETS', 'false').lower() == 'true'

FORBIDDEN_PATTERNS = [
    r'^localhost',
    r'^127\.',
    r'^0\.0\.0\.0',
    r'^169\.254\.',
    r'^10\.',
    r'^192\.168\.',
    r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',
    r'^::1',
    r'^fc00:',
    r'^fe80:',
]

# ── Circuit Breaker ───────────────────────────────────────────────────────────
_circuit_state: Dict[str, dict] = {}
_circuit_lock  = threading.Lock()


def _cb_is_open(target: str, cfg: dict) -> bool:
    if not cfg.get('enabled', True):
        return False
    threshold = cfg.get('failure_threshold', 3)
    recovery  = cfg.get('recovery_timeout', 60)
    with _circuit_lock:
        state = _circuit_state.get(target, {})
        if state.get('failures', 0) >= threshold:
            opened_at = state.get('opened_at', 0)
            if time.time() - opened_at < recovery:
                return True
            _circuit_state[target] = {'failures': 0, 'opened_at': 0}
    return False


def _cb_record_failure(target: str) -> None:
    with _circuit_lock:
        state = _circuit_state.setdefault(target, {'failures': 0, 'opened_at': 0})
        state['failures']  = state.get('failures', 0) + 1
        state['opened_at'] = time.time()
        logger.warning("Circuit breaker: %d fallos para %s", state['failures'], target[:80])


def _cb_record_success(target: str) -> None:
    with _circuit_lock:
        _circuit_state.pop(target, None)


def _validate_target_reachability(target: str, cfg: dict) -> tuple:
    timeout = cfg.get('timeout', 10)
    try:
        parsed   = urlparse(target)
        hostname = parsed.hostname
        port     = parsed.port or (443 if parsed.scheme == 'https' else 80)
        if not hostname:
            return False, 'No se pudo extraer hostname del target'
        if cfg.get('check_dns', True):
            try:
                socket.getaddrinfo(hostname, None)
            except (socket.gaierror, socket.herror) as e:
                return False, f'DNS no resuelve para {hostname}: {e}'
        if cfg.get('check_reachability', True):
            try:
                with socket.create_connection((hostname, port), timeout=timeout):
                    pass
            except (socket.timeout, ConnectionRefusedError, OSError) as e:
                return False, f'Host no alcanzable {hostname}:{port}: {e}'
        return True, 'ok'
    except Exception as e:
        return False, f'Error en validación de target: {e}'


def _build_dry_run_scan(job_id: str, target: str, scan_data: dict) -> dict:
    mock = dict(scan_data)
    mock['status']  = 'completed'
    mock['endTime'] = datetime.utcnow().isoformat() + 'Z'
    mock['dry_run'] = True
    mock['technologies'] = [
        {'name': 'Nginx',  'version': '1.25.0', 'category': 'server',     'confidence': 100},
        {'name': 'jQuery', 'version': '3.7.1',  'category': 'javascript', 'confidence': 90},
    ]
    mock['ports'] = [
        {'port': 80,  'protocol': 'tcp', 'state': 'open', 'service': 'http',  'product': 'nginx'},
        {'port': 443, 'protocol': 'tcp', 'state': 'open', 'service': 'https', 'product': 'nginx'},
    ]
    mock['directories'] = [
        {'path': '/admin', 'status': 403, 'type': 'directory'},
        {'path': '/login', 'status': 200, 'type': 'page'},
        {'path': '/api',   'status': 200, 'type': 'directory'},
    ]
    mock['vulnerabilities'] = [
        {'name': '[DRY-RUN] X-Frame-Options header missing',
         'risk': 'medium', 'tool': 'zap',
         'description': 'Simulado — no se ejecutó ZAP real'},
    ]
    mock['score'] = {
        'total': 72, 'grade': 'C',
        'breakdown': {'critical': 0, 'high': 0, 'medium': 1, 'low': 0, 'info': 2},
        'riskLevel': 'MEDIUM',
    }
    for step in mock.get('steps', []):
        step['status']   = 'completed'
        step['progress'] = 100
    return mock


# ── Storage ───────────────────────────────────────────────────────────────────
scans_fallback: Dict[str, dict] = {}
_fallback_lock = threading.Lock()
_redis_ok_until: float = 0.0
_redis_last_state: str = 'memory'
_redis_status_lock = threading.Lock()
# FIX: límite para evitar OOM cuando Redis no está disponible
_FALLBACK_MAX_SCANS = 200

# ── Orchestrator ──────────────────────────────────────────────────────────────
orchestrator = SecurityOrchestrator(
    zap_api_key=ZAP_API_KEY,
    zap_api_url=ZAP_API_URL,
    msf_host=MSF_HOST,
    msf_port=MSF_PORT,
    msf_password=MSF_PASSWORD,
)

# ── Auth decorator ────────────────────────────────────────────────────────────
def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if API_TOKEN:
            token = (
                request.headers.get('X-API-Token')
                or request.args.get('api_token')
            )
            if token != API_TOKEN:
                logger.warning(
                    "Intento de acceso no autorizado a %s desde %s",
                    request.path, request.remote_addr,
                )
                return jsonify({'error': _t('errors.unauthorized')}), 401
        return f(*args, **kwargs)
    return decorated

# ── Validación ────────────────────────────────────────────────────────────────
def validate_scan_id(scan_id: str) -> bool:
    try:
        uuid_module.UUID(scan_id, version=4)
        return True
    except (ValueError, AttributeError):
        return False


def is_allowed_target(target: str) -> tuple:
    try:
        parsed   = urlparse(target if '://' in target else f'http://{target}')
        hostname = parsed.hostname or target
        if any(
            hostname == allowed or hostname.startswith(allowed.split(':')[0])
            for allowed in ALLOWED_LAB_TARGETS
        ):
            return True, "Lab target allowed"
        if RESTRICT_TO_LAB:
            return False, (
                "Solo se permiten targets de laboratorio en modo restringido. "
                f"Targets permitidos: {', '.join(ALLOWED_LAB_TARGETS)}"
            )
        if any(c in target for c in ['@', ' ', '\\', '\n', '\r']):
            return False, "Target contains invalid characters"
        for pattern in FORBIDDEN_PATTERNS:
            if re.match(pattern, hostname, re.IGNORECASE):
                return False, f"Target matches forbidden pattern: {pattern}"
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return False, "Private/loopback IP addresses are not allowed"
        except ValueError:
            pass
        return True, "Target allowed"
    except Exception as e:
        return False, f"Target validation error: {e}"

# ── Storage helpers ───────────────────────────────────────────────────────────
def get_scan_storage() -> str:
    global _redis_ok_until, _redis_last_state
    with _redis_status_lock:
        now = time.time()
        if now < _redis_ok_until:
            return _redis_last_state
        try:
            redis_client.ping()
            _redis_last_state = 'redis'
        except Exception:
            _redis_last_state = 'memory'
        _redis_ok_until = now + 10.0
        return _redis_last_state


def save_scan(scan_id: str, scan_data: dict) -> None:
    status = scan_data.get('status', 'running')
    ttl    = 86400 if status == 'completed' else 3600
    if get_scan_storage() == 'redis':
        try:
            redis_client.setex(f"scan:{scan_id}", ttl, json.dumps(scan_data))
            return
        except Exception:
            pass
    with _fallback_lock:
        # FIX: evitar OOM — eliminar el scan más antiguo si se supera el límite
        if scan_id not in scans_fallback and len(scans_fallback) >= _FALLBACK_MAX_SCANS:
            oldest_key = next(iter(scans_fallback))
            del scans_fallback[oldest_key]
            logger.warning("Fallback storage lleno — eliminado scan más antiguo: %s", oldest_key)
        scans_fallback[scan_id] = scan_data


def get_scan(scan_id: str) -> Optional[dict]:
    if get_scan_storage() == 'redis':
        try:
            data = redis_client.get(f"scan:{scan_id}")
            if data:
                return json.loads(data)
        except Exception:
            pass
    with _fallback_lock:
        return scans_fallback.get(scan_id)


def list_scans() -> List[dict]:
    if get_scan_storage() == 'redis':
        try:
            keys  = redis_client.keys("scan:*")
            scans = []
            for key in keys:
                data = redis_client.get(key)
                if data:
                    try:
                        scans.append(json.loads(data))
                    except json.JSONDecodeError:
                        pass
            return scans
        except Exception:
            pass
    with _fallback_lock:
        return list(scans_fallback.values())


def update_step(job_id: str, step_name: str, status: str, progress: int = 0) -> None:
    scan = get_scan(job_id)
    if not scan:
        return
    for step in scan.get('steps', []):
        if step['name'] == step_name:
            step['status']   = status
            step['progress'] = progress
            if status == 'running':
                step['startTime'] = int(time.time() * 1000)
            elif status in ('completed', 'error'):
                step['endTime'] = int(time.time() * 1000)
            break
    save_scan(job_id, scan)


def _persist_step_result(job_id: str, field: str, value) -> None:
    fresh = get_scan(job_id)
    if fresh:
        fresh[field] = value
        save_scan(job_id, fresh)

# ── run_scan ──────────────────────────────────────────────────────────────────
def run_scan(job_id: str, target: str, options: dict):
    """
    Pipeline completo de escaneo v5.0.

    ORDEN DE PASOS:
      1.  Wappalyzer
      2.  Nmap
      3.  Patator     ← brute force + extrae session_cookie
      4.  Metasploit
      5.  ffuf
      6.  Gobuster
      7.  ZAP Full Scan (spider + active)
      8.  Nuclei      ← recibe session_cookie de Paso 3
      9.  Injection Scanner (10 técnicas) / SQLMap fallback
      10. Searchsploit
      11. Scoring
    """
    try:
        tools = options.get('tools', {})

        # Normalizar: 'zap' del frontend activa el full scan unificado
        if tools.get('zap'):
            tools['zap_full'] = True

        # Pre-inicializar variables
        technologies:        list = []
        ports:               list = []
        directories:         list = []
        vulnerabilities:     list = []
        exploits:            list = []
        msf_results:         list = []
        nuclei_findings:     list = []
        sqli_results:        list = []
        brute_force_results: list = []
        ffuf_endpoints:      list = []
        spider_results:      list = []

        # ── Auto-login: obtener cookie/token para labs conocidos ──────────────
        session_cookie  = None
        _auth_timestamp = time.time()   # Marca de tiempo del último login exitoso
        _SESSION_TTL    = 20 * 60       # Refrescar si han pasado >20 minutos

        def _refresh_session_if_needed(label: str = '') -> None:
            """
            Refresca la cookie si han pasado más de _SESSION_TTL segundos
            desde el último login. Actualiza session_cookie en el closure.
            Solo actúa para DVWA y WebGoat — Juice Shop usa JWT de 3h.
            """
            nonlocal session_cookie, _auth_timestamp
            t_lower = target.lower()
            # Juice Shop: JWT dura 3h, no necesita refresco
            if 'juice' in t_lower or '3001' in t_lower or '3000' in t_lower:
                return
            elapsed = time.time() - _auth_timestamp
            if elapsed < _SESSION_TTL:
                return
            logger.info(
                "Reautenticando para %s antes de %s (elapsed=%.0fs)",
                target, label, elapsed,
            )
            try:
                fresh = orchestrator._get_session_for_target(target)
                if fresh.get('cookie'):
                    session_cookie  = fresh['cookie']
                    _auth_timestamp = time.time()
                    logger.info("Reautenticación exitosa — nueva cookie obtenida")
                else:
                    logger.warning("Reautenticación fallida — usando cookie anterior")
            except Exception as _re:
                logger.warning("Error en reautenticación: %s", _re)

        auth_info = orchestrator._get_session_for_target(target)
        if auth_info.get('cookie'):
            session_cookie = auth_info['cookie']
            if auth_info.get('user_agent'):
                t = target.lower()
                if 'webgoat' in t or '3003' in t:
                    try:
                        orchestrator.zap.zap.core.set_option_default_user_agent(
                            auth_info['user_agent']
                        )
                        logger.info("ZAP User-Agent actualizado para WebGoat")
                    except Exception as e:
                        logger.debug("No se pudo actualizar UA en ZAP: %s", e)
            logger.info("Auto-login exitoso — cookie disponible para todas las herramientas")

        # ── Paso 1: Wappalyzer ────────────────────────────────────────────────
        if tools.get('wappalyzer', False):
            update_step(job_id, 'Wappalyzer', 'running')
            try:
                technologies = orchestrator.run_wappalyzer(target)
                _persist_step_result(job_id, 'technologies', technologies)
                update_step(job_id, 'Wappalyzer', 'completed', 100)
            except Exception as e:
                logger.error("Wappalyzer failed: %s", e)
                update_step(job_id, 'Wappalyzer', 'error', 0)
        else:
            update_step(job_id, 'Wappalyzer', 'completed', 100)

        # ── Paso 2: Nmap ──────────────────────────────────────────────────────
        if tools.get('nmap', False):
            update_step(job_id, 'Nmap', 'running')
            try:
                ports = orchestrator.run_nmap(target)
                _persist_step_result(job_id, 'ports', ports)
                update_step(job_id, 'Nmap', 'completed', 100)
            except Exception as e:
                logger.error("Nmap failed: %s", e)
                update_step(job_id, 'Nmap', 'error', 0)
        else:
            update_step(job_id, 'Nmap', 'completed', 100)

        # ── Paso 3: Patator — brute force + obtener cookie ────────────────────
        # Cookie disponible para pasos 4-10
        if tools.get('patator', False):
            update_step(job_id, 'Patator', 'running')
            try:
                patator_path        = options.get('login_path') or None
                brute_force_results = orchestrator.run_patator(
                    target, form_path=patator_path)
                _persist_step_result(job_id, 'brute_force_results', brute_force_results)
                for bf in brute_force_results:
                    if bf.get('success'):
                        for cred in bf.get('credentials', []):
                            if cred.get('session_cookie'):
                                session_cookie = cred['session_cookie']
                                logger.info("Cookie obtenida via Patator para %s", target)
                                break
                update_step(job_id, 'Patator', 'completed', 100)
            except Exception as e:
                logger.error("Patator failed: %s", e)
                update_step(job_id, 'Patator', 'error', 0)
        else:
            update_step(job_id, 'Patator', 'completed', 100)

        # ── Paso 4: Metasploit ────────────────────────────────────────────────
        if tools.get('metasploit', False):
            update_step(job_id, 'Metasploit', 'running')
            try:
                msf_results = orchestrator.run_metasploit(
                    target, ports=ports, technologies=technologies)
                _persist_step_result(job_id, 'metasploit', msf_results)
                update_step(job_id, 'Metasploit', 'completed', 100)
            except Exception as e:
                logger.error("Metasploit failed: %s", e)
                update_step(job_id, 'Metasploit', 'error', 0)
        else:
            update_step(job_id, 'Metasploit', 'completed', 100)

        # ── Paso 5: ffuf ──────────────────────────────────────────────────────
        if tools.get('ffuf', False):
            update_step(job_id, 'ffuf', 'running')
            try:
                t = target.lower()
                fuzz_path = '/WebGoat/FUZZ' if ('webgoat' in t or '8080' in t) else '/FUZZ'
                ffuf_endpoints = orchestrator.run_ffuf(
                    target, fuzz_path=fuzz_path, cookie=session_cookie)
                _persist_step_result(job_id, 'ffuf_endpoints', ffuf_endpoints)
                update_step(job_id, 'ffuf', 'completed', 100)
            except Exception as e:
                logger.error("ffuf failed: %s", e)
                update_step(job_id, 'ffuf', 'error', 0)
        else:
            update_step(job_id, 'ffuf', 'completed', 100)

        # ── Paso 6: Gobuster ──────────────────────────────────────────────────
        if tools.get('gobuster', False):
            update_step(job_id, 'Gobuster', 'running')
            try:
                t = target.lower()
                gobuster_target = (f"{target.rstrip('/')}/WebGoat"
                                   if ('webgoat' in t or '8080' in t) else target)
                directories = orchestrator.run_gobuster(
                    gobuster_target, cookie=session_cookie)
                _persist_step_result(job_id, 'directories', directories)
                update_step(job_id, 'Gobuster', 'completed', 100)
            except Exception as e:
                logger.error("Gobuster failed: %s", e)
                update_step(job_id, 'Gobuster', 'error', 0)
        else:
            update_step(job_id, 'Gobuster', 'completed', 100)

        # ── Paso 7: ZAP Full Scan ─────────────────────────────────────────────
        _refresh_session_if_needed('ZAP')   # ← reautentica si la sesión expiró
        if tools.get('zap', False) or tools.get('zap_full', False):
            update_step(job_id, 'ZAP Spider', 'running')
            update_step(job_id, 'ZAP', 'running')
            try:
                extra_urls = []
                for group in ffuf_endpoints:
                    for ep in group.get('endpoints', []):
                        u = ep.get('url', '')
                        if u: extra_urls.append(u)
                for d in directories:
                    path = d.get('path', '')
                    if path and not d.get('is_false_positive'):
                        extra_urls.append(f"{target.rstrip('/')}{path}")

                if extra_urls:
                    logger.info("Inyectando %d URLs en ZAP", len(extra_urls))
                    # FIX: protegido con hasattr()
                    if hasattr(orchestrator.zap, 'inject_urls'):
                        orchestrator.zap.inject_urls(extra_urls)
                    else:
                        import requests as _req
                        for _url in extra_urls[:50]:
                            try:
                                _req.get(
                                    f"{ZAP_API_URL}/JSON/core/action/accessUrl/",
                                    params={'apikey': ZAP_API_KEY, 'url': _url,
                                            'followRedirects': 'true'},
                                    timeout=5,
                                )
                            except Exception:
                                pass

                zap_result      = orchestrator.run_zap_full(target, cookie=session_cookie)
                spider_results  = [{'url': u} for u in zap_result.get('urls_descubiertas', [])]
                vulnerabilities = zap_result.get('vulnerabilidades', [])
                _persist_step_result(job_id, 'spider_results',  spider_results)
                _persist_step_result(job_id, 'vulnerabilities', vulnerabilities)
                update_step(job_id, 'ZAP Spider', 'completed', 100)
                update_step(job_id, 'ZAP',        'completed', 100)
                logger.info("ZAP completado: %d URLs, %d vulns",
                            len(spider_results), len(vulnerabilities))
            except Exception as e:
                logger.error("ZAP Full Scan failed: %s", e)
                update_step(job_id, 'ZAP Spider', 'error', 0)
                update_step(job_id, 'ZAP',        'error', 0)
        else:
            update_step(job_id, 'ZAP Spider', 'completed', 100)
            update_step(job_id, 'ZAP',        'completed', 100)

        # ── Paso 8: Nuclei ────────────────────────────────────────────────────
        # Cookie disponible desde Paso 3 (Patator o auto-login)
        _refresh_session_if_needed('Nuclei')   # ← reautentica si la sesión expiró
        if tools.get('nuclei', False):
            update_step(job_id, 'Nuclei', 'running')
            try:
                nuclei_findings = orchestrator.run_nuclei(
                    target, cookie=session_cookie)
                # FIX: nombre de campo correcto (antes: nikto_findings)
                _persist_step_result(job_id, 'nuclei_findings', nuclei_findings)
                update_step(job_id, 'Nuclei', 'completed', 100)
            except Exception as e:
                logger.error("Nuclei failed: %s", e)
                update_step(job_id, 'Nuclei', 'error', 0)
        else:
            update_step(job_id, 'Nuclei', 'completed', 100)

        # ── Paso 9: Injection Scanner / SQLMap ───────────────────────────────
        # InjectionScanner cubre 10 técnicas. Si no está instalado, usa SQLMap.
        _refresh_session_if_needed('InjectionScanner')   # ← reautentica si expiró
        if tools.get('sqlmap', False) or tools.get('injection', False):
            update_step(job_id, 'SQLMap', 'running')
            try:
                current = get_scan(job_id) or {}

                # Preferir cookie de Patator sobre auto-login
                patator_cookie = None
                for bf in current.get('brute_force_results', []):
                    if bf.get('success'):
                        for cred in bf.get('credentials', []):
                            if cred.get('session_cookie'):
                                patator_cookie = cred['session_cookie']
                                break
                if patator_cookie:
                    session_cookie = patator_cookie

                sqli_results = orchestrator.run_injection_scan(
                    target,
                    cookie=session_cookie,
                    techniques=options.get('injection_techniques', None),
                )
                _persist_step_result(job_id, 'sqli_results', sqli_results)
                update_step(job_id, 'SQLMap', 'completed', 100)
            except Exception as e:
                logger.error("Injection scan failed: %s", e)
                update_step(job_id, 'SQLMap', 'error', 0)
        else:
            update_step(job_id, 'SQLMap', 'completed', 100)

        # ── Paso 10: Searchsploit ─────────────────────────────────────────────
        if tools.get('searchsploit', False):
            update_step(job_id, 'Searchsploit', 'running')
            try:
                current = get_scan(job_id) or {}

                # Extraer CVEs desde nuclei_findings para correlación directa
                _nuclei_cves: List[str] = []
                for nf in current.get('nuclei_findings', []):
                    _tid = nf.get('template_id', '').lower()
                    if _tid.startswith('cve-') and len(_tid) >= 12:
                        _nuclei_cves.append(_tid.upper())

                exploits = orchestrator.search_exploits(
                    current.get('technologies', technologies),
                    current.get('ports', ports),
                    target=target,
                    known_cves=_nuclei_cves,
                )
                _persist_step_result(job_id, 'exploits', exploits)
                update_step(job_id, 'Searchsploit', 'completed', 100)
            except Exception as e:
                logger.error("Searchsploit failed: %s", e)
                update_step(job_id, 'Searchsploit', 'error', 0)
        else:
            update_step(job_id, 'Searchsploit', 'completed', 100)

        # ── Paso 11: Scoring ──────────────────────────────────────────────────
        update_step(job_id, 'Scoring', 'running')
        try:
            current = get_scan(job_id) or {}
            all_vulnerabilities = [
                v for v in (
                    current.get('vulnerabilities', vulnerabilities) +
                    current.get('sqli_results', []) +
                    current.get('nuclei_findings', []) +
                    current.get('metasploit', [])
                )
                if not v.get('simulated', False)
            ]
            score = calculate_security_score(
                all_vulnerabilities,
                current.get('exploits', exploits),
                brute_force_results=current.get('brute_force_results', []),
            )
            _persist_step_result(job_id, 'score', score)
            update_step(job_id, 'Scoring', 'completed', 100)
        except Exception as e:
            logger.error("Scoring failed: %s", e)
            update_step(job_id, 'Scoring', 'error', 0)

        # ── Finalizar ─────────────────────────────────────────────────────────
        final_scan            = get_scan(job_id) or {}
        final_scan['status']  = 'completed'
        final_scan['endTime'] = datetime.utcnow().isoformat()
        save_scan(job_id, final_scan)
        _cb_record_success(target)
        logger.info("Scan %s completed for target %s", job_id, target[:80])

    except Exception as e:
        logger.error("Critical scan failure for %s: %s", job_id, e)
        _cb_record_failure(target)
        failed_scan            = get_scan(job_id) or {}
        failed_scan['status']  = 'error'
        failed_scan['error']   = str(e)
        failed_scan['endTime'] = datetime.utcnow().isoformat()
        save_scan(job_id, failed_scan)

# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.route('/api/health', methods=['GET'])
@limiter.exempt
def health_check():
    storage_status = get_scan_storage()
    return jsonify({
        'status':         'healthy',
        'version':        '5.0.0',
        'storage':        'connected' if storage_status == 'redis' else 'fallback',
        'zap_configured': bool(ZAP_API_KEY),
        'tools': [
            'wappalyzer', 'nmap', 'gobuster', 'zap', 'searchsploit',
            'metasploit', 'nuclei', 'sqlmap', 'injection_scanner', 'patator', 'ffuf',
        ],
    })


@app.route('/api/scan', methods=['POST'])
@require_token
@limiter.limit("20 per hour")
def start_scan():
    """Inicia un escaneo de seguridad. Devuelve jobId inmediatamente."""
    data = request.get_json(silent=True)
    if not data:
        _t = get_t(locale_from_request(request))
        return jsonify({'error': _t('errors.invalidJson')}), 400

    target = data.get('target', '').strip()
    if not target:
        _t = get_t(locale_from_request(request))
        return jsonify({'error': _t('errors.targetRequired')}), 400

    options = data.get('options', {}) or {}

    if 'tools' not in options and 'tools' in data:
        options['tools'] = data['tools']
    if 'intensity' not in options and 'intensity' in data:
        options['intensity'] = data['intensity']

    dry_run   = bool(options.get('dry_run', False))
    cb_config = options.get('circuit_breaker', {}) or {}
    tv_config = options.get('target_validation', {}) or {}
    retry_cfg = options.get('retry_config', {}) or {}

    # Normalizar camelCase → snake_case
    if 'checkDns'          in tv_config: tv_config['check_dns']         = tv_config.pop('checkDns')
    if 'checkReachability' in tv_config: tv_config['check_reachability'] = tv_config.pop('checkReachability')
    if 'failureThreshold'  in cb_config: cb_config['failure_threshold']  = cb_config.pop('failureThreshold')
    if 'recoveryTimeout'   in cb_config: cb_config['recovery_timeout']   = cb_config.pop('recoveryTimeout')
    if 'maxRetries'        in retry_cfg: retry_cfg['max_retries']        = retry_cfg.pop('maxRetries')
    if 'backoffFactor'     in retry_cfg: retry_cfg['backoff_factor']     = retry_cfg.pop('backoffFactor')

    if _cb_is_open(target, cb_config):
        return jsonify({
            'error':  get_t(locale_from_request(request))('errors.circuitBreaker'),
            'reason': 'circuit_breaker_open',
        }), 429

    if not dry_run and (tv_config.get('check_dns', True) or tv_config.get('check_reachability', True)):
        ok, reason_tv = _validate_target_reachability(target, tv_config)
        if not ok:
            _cb_record_failure(target)
            return jsonify({
                'error':  get_t(locale_from_request(request))('errors.targetUnreachable', reason=reason_tv),
                'reason': 'target_unreachable',
            }), 422

    is_allowed, reason = is_allowed_target(target)
    if not is_allowed:
        return jsonify({
            'error':           'Target not allowed',
            'reason':          reason,
            'allowed_targets': ALLOWED_LAB_TARGETS,
        }), 403

    job_id    = str(uuid.uuid4())
    scan_data = {
        'id':        job_id,
        'target':    target,
        'options':   options,
        'status':    'running',
        'startTime': datetime.utcnow().isoformat() + 'Z',
        'endTime':   None,
        'steps': [
            {'name': 'Wappalyzer',   'status': 'pending', 'progress': 0},
            {'name': 'Nmap',         'status': 'pending', 'progress': 0},
            {'name': 'Patator',      'status': 'pending', 'progress': 0},
            {'name': 'Metasploit',   'status': 'pending', 'progress': 0},
            {'name': 'ffuf',         'status': 'pending', 'progress': 0},
            {'name': 'Gobuster',     'status': 'pending', 'progress': 0},
            {'name': 'ZAP Spider',   'status': 'pending', 'progress': 0},
            {'name': 'ZAP',          'status': 'pending', 'progress': 0},
            {'name': 'Nuclei',       'status': 'pending', 'progress': 0},
            {'name': 'SQLMap',       'status': 'pending', 'progress': 0},
            {'name': 'Searchsploit', 'status': 'pending', 'progress': 0},
            {'name': 'Scoring',      'status': 'pending', 'progress': 0},
        ],
        'technologies':        [],
        'ports':               [],
        'directories':         [],
        'spider_results':      [],
        'vulnerabilities':     [],
        'exploits':            [],
        'metasploit':          [],
        'nuclei_findings':     [],
        'sqli_results':        [],
        'brute_force_results': [],
        'ffuf_endpoints':      [],
        'score': {
            'total': 0, 'grade': 'A',
            'breakdown': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0},
        },
        'dry_run':           dry_run,
        'circuit_breaker':   cb_config,
        'target_validation': tv_config,
        'retry_config':      retry_cfg,
    }

    save_scan(job_id, scan_data)

    if dry_run:
        mock_scan = _build_dry_run_scan(job_id, target, scan_data)
        save_scan(job_id, mock_scan)
        logger.info("Dry-run scan %s completado para %s", job_id, target[:80])
        return jsonify({'jobId': job_id, 'status': 'completed', 'dry_run': True})

    # FIX: daemon=False — el thread sobrevive al worker de gunicorn
    thread = threading.Thread(
        target=run_scan,
        args=(job_id, target, options),
        daemon=False,
    )
    thread.start()

    logger.info("Started scan %s for target %s", job_id, target[:80])
    return jsonify({'jobId': job_id, 'status': 'running'})


@app.route('/api/scan/<scan_id>/status', methods=['GET'])
@limiter.exempt
@require_token
def get_scan_status(scan_id: str):
    if not validate_scan_id(scan_id):
        return jsonify({'error': _t('errors.invalidFormat')}), 400
    scan = get_scan(scan_id)
    if not scan:
        return jsonify({'error': get_t(locale_from_request(request))('errors.scanNotFound')}), 404
    return jsonify(scan)


@app.route('/api/scan/<scan_id>/report', methods=['GET'])
@limiter.exempt
@require_token
def get_report(scan_id: str):
    if not validate_scan_id(scan_id):
        return jsonify({'error': _t('errors.invalidFormat')}), 400
    scan = get_scan(scan_id)
    if not scan:
        return jsonify({'error': get_t(locale_from_request(request))('errors.scanNotFound')}), 404
    if scan.get('status') != 'completed':
        return jsonify({'error': _t('errors.scanNotCompleted'), 'status': scan.get('status')}), 400
    format_type     = request.args.get('format', 'html').lower()
    allowed_formats = ['html', 'json', 'pdf', 'csv']
    if format_type not in allowed_formats:
        return jsonify({'error': _t('errors.formatNotAllowed', formats=', '.join(allowed_formats))}), 400
    try:
        report_path = generate_report(scan, format_type, locale_from_request(request))
        if not report_path or not os.path.exists(report_path):
            return jsonify({'error': _t('errors.reportFailed')}), 500
        return send_file(
            report_path,
            as_attachment=True,
            download_name=f'security-report-{scan_id}.{format_type}',
        )
    except Exception as e:
        logger.error("Error generating report: %s", e)
        return jsonify({'error': str(e)}), 500


@app.route('/api/history', methods=['GET'])
@require_token
def get_scan_history():
    try:
        scan_list = list_scans()
        scan_list.sort(key=lambda x: x.get('startTime', ''), reverse=True)
        return jsonify({'scans': scan_list[:100], 'total': len(scan_list)})
    except Exception as e:
        logger.error("Error retrieving history: %s", e)
        return jsonify({'error': _t('errors.historyFailed')}), 500


@app.route('/api/scan/<scan_id>', methods=['DELETE'])
@require_token
def delete_scan(scan_id: str):
    if not validate_scan_id(scan_id):
        return jsonify({'error': _t('errors.invalidFormat')}), 400
    if get_scan_storage() == 'redis':
        redis_client.delete(f"scan:{scan_id}")
    else:
        with _fallback_lock:
            scans_fallback.pop(scan_id, None)
    return jsonify({'message': get_t(locale_from_request(request))('errors.scanDeleted')})


@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify({
        'version':         '5.0.0',
        'allowed_targets': ALLOWED_LAB_TARGETS,
        'restrict_to_lab': RESTRICT_TO_LAB,
        'available_tools': [
            'wappalyzer', 'nmap', 'gobuster', 'zap', 'searchsploit',
            'metasploit', 'nuclei', 'sqlmap', 'injection_scanner', 'patator', 'ffuf',
        ],
        'report_formats': ['html', 'json', 'pdf', 'csv'],
        'metasploit': {
            'enabled': True,
            'mode':    'simulation' if getattr(orchestrator.metasploit, '_simulation', True) else 'live',
            'host':    MSF_HOST,
            'port':    MSF_PORT,
        },
    })

# ── Lab endpoints ─────────────────────────────────────────────────────────────
try:
    import docker as docker_sdk  # type: ignore
    DOCKER_AVAILABLE = True
except ImportError:
    docker_sdk = None
    DOCKER_AVAILABLE = False


def _get_docker_client():
    if not DOCKER_AVAILABLE or docker_sdk is None:
        logger.error("Docker SDK no instalado")
        return None
    try:
        return docker_sdk.from_env()
    except Exception as e:
        logger.error("Docker client error: %s", e)
        return None


LAB_CONTAINERS = {
    'juice-shop': {'image': 'bkimminich/juice-shop:latest', 'ports': {'3000/tcp': 3001}},
    'dvwa':       {'image': 'ghcr.io/digininja/dvwa:latest', 'ports': {'80/tcp':   3002}},
    'webgoat':    {'image': 'webgoat/webgoat:latest',        'ports': {'8080/tcp': 3003}},
}


@app.route('/api/lab/status', methods=['GET'])
@limiter.exempt
def lab_status():
    client = _get_docker_client()
    if not client:
        return jsonify({'error': _t('errors.dockerUnavailable')}), 500
    result = {}
    for lab_id in LAB_CONTAINERS:
        try:
            container = client.containers.get(lab_id)
            result[lab_id] = 'running' if container.status == 'running' else 'stopped'
        except docker_sdk.errors.NotFound:
            result[lab_id] = 'stopped'
        except Exception:
            result[lab_id] = 'error'
    return jsonify(result)


@app.route('/api/lab/<lab_id>/start', methods=['POST'])
@limiter.exempt
def lab_start(lab_id: str):
    if lab_id not in LAB_CONTAINERS:
        return jsonify({'error': _t('errors.labNotFound')}), 404
    client = _get_docker_client()
    if not client:
        return jsonify({'error': _t('errors.dockerUnavailable')}), 500
    cfg = LAB_CONTAINERS[lab_id]
    try:
        try:
            container = client.containers.get(lab_id)
            if container.status != 'running':
                container.start()
            return jsonify({'status': 'running', 'lab': lab_id})
        except docker_sdk.errors.NotFound:
            pass
        client.containers.run(
            cfg['image'],
            name=lab_id,
            ports=cfg['ports'],
            detach=True,
            remove=False,
            network='securescan-net',
        )
        return jsonify({'status': 'starting', 'lab': lab_id})
    except Exception as e:
        logger.error("Lab start error %s: %s", lab_id, e)
        return jsonify({'error': str(e)}), 500


@app.route('/api/lab/<lab_id>/stop', methods=['POST'])
@limiter.exempt
def lab_stop(lab_id: str):
    if lab_id not in LAB_CONTAINERS:
        return jsonify({'error': _t('errors.labNotFound')}), 404
    client = _get_docker_client()
    if not client:
        return jsonify({'error': _t('errors.dockerUnavailable')}), 500
    try:
        container = client.containers.get(lab_id)
        container.stop(timeout=10)
        return jsonify({'status': 'stopped', 'lab': lab_id})
    except docker_sdk.errors.NotFound:
        return jsonify({'status': 'stopped', 'lab': lab_id})
    except Exception as e:
        logger.error("Lab stop error %s: %s", lab_id, e)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port       = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)