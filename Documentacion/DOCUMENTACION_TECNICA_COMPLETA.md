# DOCUMENTACIÓN TÉCNICA COMPLETA
## SecureScan Pro v5.0 — Plataforma Automatizada de Análisis de Seguridad Web

**Autor:** Tecnico en Seguridad de Aplicaciones Web  
**Institución:** SENA — Servicio Nacional de Aprendizaje (Colombia)  
**Programa:** Técnico en Seguridad de Aplicaciones Web  
**Versión del sistema:** 5.0.0  
**Fecha de actualización:** Junio 2026  

---

## TABLA DE CONTENIDOS

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Arquitectura General del Sistema](#2-arquitectura-general-del-sistema)
3. [Estructura de Directorios del Proyecto](#3-estructura-de-directorios-del-proyecto)
4. [Backend — Flask API (server/app.py)](#4-backend--flask-api-serverapppy)
5. [Orquestador de Seguridad (server/modules/orchestrator.py)](#5-orquestador-de-seguridad-servermodulesorchestratorrpy)
6. [Módulos de Seguridad — Descripción Técnica Detallada](#6-módulos-de-seguridad--descripción-técnica-detallada)
7. [Utilidades del Backend (server/utils/)](#7-utilidades-del-backend-serverutils)
8. [Frontend — Next.js / React](#8-frontend--nextjs--react)
9. [Infraestructura Docker y Docker Compose](#9-infraestructura-docker-y-docker-compose)
10. [Pipeline de Escaneo — Flujo Completo de 11 Pasos](#10-pipeline-de-escaneo--flujo-completo-de-11-pasos)
11. [API REST — Referencia de Endpoints](#11-api-rest--referencia-de-endpoints)
12. [Variables de Entorno y Configuración](#12-variables-de-entorno-y-configuración)
13. [Laboratorio de Seguridad — Targets Vulnerables](#13-laboratorio-de-seguridad--targets-vulnerables)
14. [Sistema de Puntuación de Seguridad](#14-sistema-de-puntuación-de-seguridad)
15. [Generación de Reportes](#15-generación-de-reportes)
16. [Mecanismos de Resiliencia y Seguridad](#16-mecanismos-de-resiliencia-y-seguridad)
17. [Scripts de Automatización](#17-scripts-de-automatización)
18. [Dependencias y Stack Tecnológico Completo](#18-dependencias-y-stack-tecnológico-completo)
19. [Correcciones Acumuladas v5.0 — Registro Técnico](#19-correcciones-acumuladas-v50--registro-técnico)

---

## 1. RESUMEN EJECUTIVO

SecureScan Pro v5.0 es una plataforma de análisis de seguridad web de código abierto orientada a entornos de laboratorio educativos. Integra once herramientas de pentesting reales dentro de un pipeline automatizado y secuencial de once pasos, todo coordinado por un orquestador central en Python. Los resultados se consolidan en un dashboard interactivo desarrollado en Next.js 14, con soporte para generación de reportes en cuatro formatos (HTML, PDF, JSON, CSV).

La plataforma está concebida específicamente como proyecto de grado del programa **Técnico en Seguridad de Aplicaciones Web del SENA**, demostrando la integración real de herramientas de la industria —nmap, OWASP ZAP, SQLMap, Nuclei, Gobuster, ffuf, Patator, Metasploit, Searchsploit y Wappalyzer— en un único sistema coherente, completamente contenedorizado con Docker Compose.

**Características clave de la versión 5.0:**

- Pipeline de 11 pasos con propagación automática de cookies de sesión entre herramientas (desde el Paso 3 hasta el Paso 10).
- Módulo `InjectionScanner` propio que cubre 10 técnicas de inyección activa (SQLi, NoSQLi, XPath, XXE, XSS, Command Injection, Path Traversal, SSRF, SSTI, LDAP).
- Auto-login específico para cada laboratorio (DVWA con corrección de CSRF token, Juice Shop con JWT, WebGoat con Spring Security).
- Circuit Breaker en doble capa (aplicación Flask y orquestador) para resiliencia ante fallos de red.
- Almacenamiento dual Redis / fallback en memoria con límite anti-OOM de 200 entradas.
- Validación estricta de targets con UUID v4 para scan IDs, autenticación por token API y rate limiting via Flask-Limiter.
- Gunicorn con `worker-class sync`, `--threads 4`, timeout configurable (default 3600s) para soportar escaneos largos.

---

## 2. ARQUITECTURA GENERAL DEL SISTEMA

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USUARIO (Navegador)                          │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTP :3000
┌────────────────────────────▼────────────────────────────────────────┐
│              FRONTEND — Next.js 14 / React 18 / TypeScript          │
│  ┌──────────────┐  ┌─────────────────┐  ┌────────────────────────┐ │
│  │  scan-form   │  │  scan-progress  │  │  results-dashboard     │ │
│  │  .tsx        │  │  .tsx           │  │  .tsx                  │ │
│  └──────────────┘  └─────────────────┘  └────────────────────────┘ │
│  lib/api-client.ts — lib/scan-context.tsx — components/ui/ (Shadcn) │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTP :5000 (REST JSON)
┌────────────────────────────▼────────────────────────────────────────┐
│         BACKEND — Flask 3.x / Gunicorn / Python 3.11                │
│                     server/app.py                                    │
│  ┌───────────────────┐  ┌────────────────┐  ┌──────────────────┐   │
│  │  Autenticación    │  │  Rate Limiting  │  │  Validación      │   │
│  │  (X-API-Token)    │  │  Flask-Limiter  │  │  UUID v4 / CORS  │   │
│  └───────────────────┘  └────────────────┘  └──────────────────┘   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │               SecurityOrchestrator                            │  │
│  │               server/modules/orchestrator.py                  │  │
│  │                                                               │  │
│  │  Paso 1  Wappalyzer  → Paso 2  Nmap     → Paso 3  Patator    │  │
│  │  Paso 4  Metasploit  → Paso 5  ffuf     → Paso 6  Gobuster   │  │
│  │  Paso 7  ZAP Full   → Paso 8  Nuclei   → Paso 9  Injection  │  │
│  │  Paso 10 Searchsploit → Paso 11 Scoring                       │  │
│  └───────────────────────────────────────────────────────────────┘  │
└──────┬────────────────────────┬──────────────────────────┬──────────┘
       │                        │                          │
┌──────▼──────┐  ┌─────────────▼──────────────┐  ┌────────▼────────┐
│   Redis 7   │  │  OWASP ZAP :8080           │  │  SQLMap API     │
│   :6379     │  │  (container: zap)          │  │  :8775          │
│  (sesiones  │  │  Spider + Active Scan      │  │  (container:    │
│   / cache)  │  │                            │  │  sqlmapapi)     │
└─────────────┘  └────────────────────────────┘  └─────────────────┘
┌─────────────────────────────────────────────────────────────────────┐
│                   RED DE LABORATORIO (lab-net)                       │
│  ┌─────────────────┐  ┌─────────────┐  ┌──────────────────────────┐│
│  │  Juice Shop     │  │    DVWA     │  │       WebGoat            ││
│  │  :3001 → :3000  │  │:3002 → :80 │  │   :3003 → :8080          ││
│  │  (Node.js/Koa)  │  │(PHP+MariaDB)│  │  (Java Spring Boot)      ││
│  └─────────────────┘  └─────────────┘  └──────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │  Metasploit RPC — msfrpcd :55553 (container: securescan-msfrpcd)││
│  └─────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

**Redes Docker:**

| Red | Subnet | Propósito |
|---|---|---|
| `securescan-net` | `172.20.0.0/16` | Comunicación interna entre servicios principales (API, Redis, ZAP, MSF) |
| `lab-net` | `172.21.0.0/16` | Aislamiento de los targets vulnerables del laboratorio |

---

## 3. ESTRUCTURA DE DIRECTORIOS DEL PROYECTO

```
SecureScan-main/
├── server/                          # Backend Python/Flask
│   ├── app.py                       # Aplicación Flask principal (v5.0, 1010 líneas)
│   ├── Dockerfile                   # Imagen backend — python:3.11-slim-bookworm
│   ├── entrypoint.sh                # Script de arranque con inicialización robusta
│   ├── requirements.txt             # Dependencias Python del backend
│   ├── wordlist-common.txt          # Wordlist incluida para Gobuster/ffuf
│   ├── modules/                     # Módulos de herramientas de seguridad
│   │   ├── __init__.py
│   │   ├── wappalyzer.py            # Huella tecnológica (python-Wappalyzer)
│   │   ├── nmap_scanner.py          # Escaneo de puertos y servicios
│   │   ├── zap_scanner.py           # DAST con OWASP ZAP (spider + active)
│   │   ├── nuclei.py                # Escaneo por plantillas (v3.2.4)
│   │   ├── sqlmap.py                # Detección SQL Injection (Enterprise)
│   │   ├── ffuf.py                  # Fuzzing de endpoints (v2.1.0)
│   │   ├── gobuster.py              # Enumeración de directorios (v3.6.0)
│   │   ├── metasploit.py            # Exploits via Console RPC
│   │   ├── searchsploit.py          # Búsqueda en ExploitDB local
│   │   ├── patator.py               # Fuerza bruta multi-protocolo
│   │   ├── injection_scanner.py     # Motor propio — 10 técnicas de inyección
│   │   └── orchestrator.py          # Pipeline central de 12 fases (1107 líneas)
│   └── utils/
│       ├── __init__.py
│       ├── reporter.py              # Generación de reportes HTML/PDF/JSON/CSV
│       └── scoring.py               # Cálculo de puntuación CVSS-like
│
├── app/                             # Next.js 14 App Router
│   ├── layout.tsx                   # Layout raíz con ThemeProvider
│   ├── globals.css                  # Estilos globales + variables CSS
│   ├── page.tsx                     # Página principal / Landing
│   ├── scanner/
│   │   └── page.tsx                 # Página principal del scanner (SPA)
│   ├── history/
│   │   └── page.tsx                 # Historial de escaneos
│   ├── lab/
│   │   └── page.tsx                 # Panel de control del laboratorio
│   ├── docs/
│   │   └── page.tsx                 # Documentación embebida
│   └── api/
│       └── docs/[slug]/route.ts     # API Route para servir docs estáticos
│
├── components/                      # Componentes React reutilizables
│   ├── header.tsx                   # Header de navegación global
│   ├── scan-form.tsx                # Formulario de inicio de escaneo
│   ├── scan-progress.tsx            # Barra de progreso en tiempo real
│   ├── results-dashboard.tsx        # Dashboard de resultados (62 KB)
│   ├── report-download-modal.tsx    # Modal de descarga de reportes
│   ├── theme-provider.tsx           # Provider de tema claro/oscuro
│   └── ui/                          # Componentes Shadcn/ui + Radix
│
├── lib/                             # Lógica cliente compartida
│   ├── api-client.ts                # Cliente HTTP tipado para la API (12 KB)
│   ├── scan-context.tsx             # React Context para estado del scan
│   ├── validators.ts                # Validación de inputs del formulario
│   └── utils.ts                     # Utilidades generales (cn, etc.)
│
├── public/
│   └── docs/                        # Documentación estática (Markdown)
│       ├── api.md
│       ├── architecture.md
│       ├── deployment.md
│       ├── security.md
│       └── tools.md
│
├── docker-compose.yml               # Orquestación completa de 10 servicios
├── Dockerfile.frontend              # Imagen frontend — node:20-alpine
├── .env.example                     # Plantilla de variables de entorno
├── start.sh                         # Script de arranque completo
├── verify.sh                        # Verificación de estado de todos los servicios
├── fix_frontend_dvwa.sh             # Corrección de DVWA para el frontend
├── package.json                     # Dependencias Node.js (pnpm)
├── pnpm-lock.yaml                   # Lockfile pnpm
├── next.config.mjs                  # Configuración Next.js
├── tailwind.config.ts               # Configuración Tailwind CSS
├── tsconfig.json                    # Configuración TypeScript
└── requirements.txt                 # Dependencias Python (raíz, para referencia)
```

---

## 4. BACKEND — FLASK API (server/app.py)

### 4.1 Versión y características generales

`server/app.py` es el punto de entrada de la API REST. Está identificado internamente como **SecureScan Pro v5.0** y expone todos los endpoints bajo el prefijo `/api/`. Corre con Gunicorn en modo `sync` con 2 workers y 4 threads por worker.

### 4.2 Inicialización y configuración

```python
# Stack de inicialización
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')   # Validado — falla si es insegura en producción
CORS(app, origins=[...])                         # Orígenes permitidos desde ALLOWED_ORIGINS
redis_client = redis.from_url(redis_url)        # Redis con contraseña
limiter = Limiter(app=app, key_func=get_remote_address, storage_uri=redis_url)
orchestrator = SecurityOrchestrator(...)        # Única instancia global
```

**Validación de `SECRET_KEY`:** Si el valor contiene la cadena `"CAMBIA"` o `"change"` y `FLASK_ENV` no es `"development"`, la aplicación falla con `RuntimeError` al arrancar. Esto garantiza que no se despliegue en producción con claves de ejemplo.

### 4.3 Sistema de almacenamiento dual (Redis / Memoria)

```python
# Cache de estado de conexión — evita ping a Redis en cada operación
_redis_ok_until: float = 0.0       # timestamp de expiración (10s)
_redis_last_state: str = 'memory'  # estado cacheado

def get_scan_storage() -> str:
    # Retorna 'redis' o 'memory' — solo hace ping cada 10 segundos
    ...

def save_scan(scan_id: str, scan_data: dict) -> None:
    # TTL: 86400s si completed, 3600s si running/error
    # Fallback en memoria con límite de 200 entradas (anti-OOM)
    ...
```

**Protecciones del fallback en memoria:**
- `threading.Lock` en todas las operaciones de escritura.
- Límite de 200 entradas (`_FALLBACK_MAX_SCANS`). Cuando se supera, elimina el scan más antiguo (FIFO) antes de insertar el nuevo.

### 4.4 Autenticación por token (X-API-Token)

```python
# Decorador @require_token aplicado a todos los endpoints sensibles
def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if API_TOKEN:
            token = (
                request.headers.get('X-API-Token')
                or request.args.get('api_token')
            )
            if token != API_TOKEN:
                return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated
```

Si `API_TOKEN` está vacío (no configurado), el decorador permite el acceso sin autenticación — emitiendo un `WARNING` en el arranque. Esto facilita el desarrollo local sin romper el flujo productivo.

### 4.5 Rate Limiting

| Endpoint | Límite |
|---|---|
| `/api/scan` (POST) | 20 solicitudes por hora |
| `/api/health` | Exento (`@limiter.exempt`) |
| `/api/scan/<id>/status` | Exento |
| `/api/scan/<id>/report` | Exento |
| `/api/lab/*` | Exento |
| Resto de endpoints | 500/día, 100/hora (default) |

### 4.6 Validación de targets

```python
FORBIDDEN_PATTERNS = [
    r'^localhost', r'^127\.', r'^0\.0\.0\.0',
    r'^169\.254\.',
    r'^10\.',              # Redes privadas clase A
    r'^192\.168\.',        # Redes privadas clase C
    r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',  # Redes privadas clase B
    r'^::1', r'^fc00:', r'^fe80:',       # IPv6 privadas/loopback
]
```

Los targets del laboratorio (`juice-shop:3000`, `dvwa:80`, `webgoat:8080`) están en la lista `ALLOWED_LAB_TARGETS` y siempre pasan la validación, independientemente de los patrones anteriores.

**Validación de UUID v4:** Antes de cualquier operación sobre un scan específico, el `scan_id` se valida con `uuid.UUID(scan_id, version=4)`. Peticiones con IDs malformados reciben `400 Bad Request`.

### 4.7 Circuit Breaker en la capa de aplicación

```python
_circuit_state: Dict[str, dict] = {}
_circuit_lock = threading.Lock()

def _cb_is_open(target: str, cfg: dict) -> bool:
    # Comprueba si el circuito está abierto para un target específico
    # cfg.failure_threshold = 3 (default), cfg.recovery_timeout = 60s (default)
    ...

def _cb_record_failure(target: str) -> None: ...
def _cb_record_success(target: str) -> None: ...
```

El circuito se abre cuando un target acumula `failure_threshold` fallos consecutivos. Permanece abierto durante `recovery_timeout` segundos. Los valores son configurables por petición a través de `options.circuit_breaker`.

### 4.8 Dry-run mode

Cuando `options.dry_run = true`, el endpoint `/api/scan` genera inmediatamente un escaneo simulado completo con datos de ejemplo (tecnologías, puertos, directorios, vulnerabilidades y puntuación), sin lanzar ninguna herramienta real. Útil para verificar que la UI funciona sin tener el laboratorio activo.

### 4.9 Threads de escaneo

```python
thread = threading.Thread(
    target=run_scan,
    args=(job_id, target, options),
    daemon=False,  # No-daemon: sobrevive al worker de Gunicorn
)
thread.start()
```

El uso de `daemon=False` garantiza que el thread de escaneo no sea matado cuando Gunicorn recicla su worker, permitiendo que escaneos largos terminen correctamente.

---

## 5. ORQUESTADOR DE SEGURIDAD (server/modules/orchestrator.py)

### 5.1 Clase SecurityOrchestrator

El orquestador es una clase Python de 1107 líneas que instancia, configura y coordina los 11 módulos de seguridad. Es la pieza central del sistema.

```python
class SecurityOrchestrator:
    TIMEOUTS = {
        'wappalyzer':   int(os.getenv('SCAN_TIMEOUT_WAPPALYZER', 60)),
        'nmap':         int(os.getenv('SCAN_TIMEOUT_NMAP', 300)),
        'ffuf':         int(os.getenv('SCAN_TIMEOUT_FFUF', 300)),
        'gobuster':     int(os.getenv('SCAN_TIMEOUT_GOBUSTER', 300)),
        'zap':          int(os.getenv('SCAN_TIMEOUT_ZAP', 1200)),
        'nuclei':       int(os.getenv('SCAN_TIMEOUT_NUCLEI', 1200)),
        'searchsploit': int(os.getenv('SCAN_TIMEOUT_SEARCHSPLOIT', 120)),
        'metasploit':   int(os.getenv('SCAN_TIMEOUT_METASPLOIT', 900)),
        'sqlmap':       int(os.getenv('SCAN_TIMEOUT_SQLMAP', 600)),
        'patator':      int(os.getenv('SCAN_TIMEOUT_PATATOR', 180)),
        'injection':    int(os.getenv('SCAN_TIMEOUT_INJECTION', 600)),
    }
```

Todos los timeouts son configurables mediante variables de entorno, lo que permite ajustarlos sin modificar código.

### 5.2 Sistema de timeout seguro con threading.Event

```python
def run_with_timeout(func, args=(), kwargs=None, seconds=300, default=None):
    """Timeout seguro — reemplaza signal.SIGALRM (no funciona en threads)."""
    result_container    = [default]
    exception_container = [None]
    finished = threading.Event()

    def target():
        try:
            result_container[0] = func(*args, **kwargs)
        except Exception as e:
            exception_container[0] = e
        finally:
            finished.set()

    t = threading.Thread(target=target, daemon=True)
    t.start()
    finished.wait(timeout=seconds)

    if not finished.is_set():
        raise ScanTimeoutError(f"Scan exceeded {seconds} seconds")
    if exception_container[0] is not None:
        raise exception_container[0]
    return result_container[0]
```

Este patrón es el correcto en Python para timeouts en entornos multi-thread, ya que `signal.SIGALRM` solo funciona en el hilo principal.

### 5.3 Retry con backoff exponencial

```python
def _run_with_retry(self, func, args=(), kwargs=None, tool_name='',
                    timeout=120, default=None, retry_cfg=None):
    cfg         = retry_cfg or {}
    max_retries = cfg.get('max_retries', 1)
    backoff     = cfg.get('backoff_factor', 1.5)
    retry_on    = set(cfg.get('retry_on', ['timeout', 'connection_error']))
    # Reintenta automáticamente en timeout y errores de conexión
    # Espera: backoff^attempt segundos entre intentos
```

### 5.4 Auto-login específico por laboratorio

El método `_get_session_for_target()` realiza login automático antes del inicio de cada escaneo, obteniendo la cookie/token de sesión que se propagará a todas las herramientas del pipeline:

| Laboratorio | Estrategia de login | Credenciales | Cookie resultante |
|---|---|---|---|
| **DVWA** | Formulario HTML + CSRF token en dos fases (login + security.php) | `admin / password` | `PHPSESSID=...; security=low` |
| **Juice Shop** | REST API JSON `/rest/user/login` | `admin@juice-sh.op / admin123` | `token=<JWT>` |
| **WebGoat** | Formulario Spring Security (GET inicial obligatorio) | `securescan / Password` | `JSESSIONID=...` |
| **Testfire** | Formulario estándar | `jsmith / demo1234` | Cookie de sesión |

**Corrección crítica v5.0 (DVWA):** `security.php` requiere su propio token CSRF (`user_token`) antes de aceptar el cambio de nivel de seguridad. Sin este token, DVWA ignoraba el cambio y mantenía el nivel `impossible`, bloqueando efectivamente SQLMap y Nuclei. La solución implementa tres peticiones secuenciales: GET login → POST login → GET security.php → POST security.php con token correcto.

**Corrección crítica v5.0 (WebGoat):** Corrección de typo `'securesacan'` → `'securescan'` en el nombre de usuario. Este error silencioso provocaba que el auto-login fallara siempre para WebGoat.

### 5.5 Propagación de cookies entre herramientas

```
_get_session_for_target() → session_cookie
          │
          ▼
Paso 3: Patator (puede sobreescribir con cookie de credencial encontrada)
          │
          ├──→ Paso 5: ffuf    (cookie=session_cookie)
          ├──→ Paso 6: Gobuster (cookie=session_cookie)
          ├──→ Paso 7: ZAP Full Scan (cookie=session_cookie)
          ├──→ Paso 8: Nuclei  (cookie=session_cookie)
          └──→ Paso 9: InjectionScanner / SQLMap (cookie=session_cookie)
```

### 5.6 Filtrado de términos irrelevantes para Searchsploit

```python
_SKIP_EXPLOIT_TERMS = {
    'country', 'ip', 'title', 'html5', 'script', 'httponly', 'cookies',
    'redirectlocation', 'x-powered-by', 'x-frame-options', 'httpserver',
    'passwordfield', 'emailfield', 'uncommonheaders', 'html-meta-author',
    'meta-generator', 'via-proxy', 'dvwa', 'email', 'bootstrap',
    'jquery', 'google-analytics', 'font-awesome',
    'java', 'python', 'ruby', 'javascript', 'typescript', 'css',
    'html', 'xml', 'json', 'http', 'https', 'tcp', 'udp', 'ssl',
    'tls', 'unix', 'linux', 'windows', 'macos',
    'debian', 'ubuntu', 'centos', 'redhat', 'fedora',
}
```

**Corrección histórica importante:** En versiones anteriores, términos como `php`, `apache`, `nginx` y `sql` estaban incorrectamente en esta lista de exclusión, lo que hacía que Searchsploit nunca encontrara exploits para las tecnologías más comunes. Fueron eliminados de la lista.

---

## 6. MÓDULOS DE SEGURIDAD — DESCRIPCIÓN TÉCNICA DETALLADA

### 6.1 Wappalyzer (`server/modules/wappalyzer.py`)

**Función:** Identificación de tecnologías web (fingerprinting).

**Estrategia de detección en cascada:**
1. `python-Wappalyzer` — librería Python, sin proceso externo, usa `Wappalyzer.analyze_with_categories(WebPage.new_from_url(target))`.
2. `wappalyzer-cli` — herramienta Node.js opcional, invocada como subproceso.
3. `_simulate_scan()` — datos por laboratorio cuando ninguna opción está disponible.

**Salida esperada:**
```json
[
  {"name": "Node.js", "version": "18.x", "category": "javascript-frameworks", "confidence": 100},
  {"name": "Express", "version": "4.x", "category": "web-frameworks", "confidence": 90}
]
```

Todos los dicts de simulación incluyen `"simulated": true` para que la UI muestre un banner de advertencia.

### 6.2 Nmap Scanner (`server/modules/nmap_scanner.py`)

**Función:** Escaneo de puertos y detección de servicios/versiones.

**Configuración de puertos dinámicos:**
- Si el puerto de la URL está en el rango 1-1000, usa el rango `1-1000`.
- Si está fuera del rango estándar (e.g., 3001 para Juice Shop), usa `1-1000,<puerto>` para asegurarse de incluirlo.

**Comando base ejecutado:**
```bash
nmap -sV -sC -O --script=banner,version -T4 -p <ports> --open -oX - <hostname>
```

**Capacidades NET_RAW:** El Dockerfile asigna `cap_net_raw,cap_net_admin+eip` al binario nmap con `setcap`, permitiendo que opere sin root completo.

**Salida esperada:**
```json
[
  {"port": 80, "protocol": "tcp", "state": "open", "service": "http",
   "product": "nginx", "version": "1.25.0", "extrainfo": ""},
  {"port": 443, "protocol": "tcp", "state": "open", "service": "https",
   "product": "nginx", "version": "1.25.0", "extrainfo": "TLSv1.3"}
]
```

**Validación de targets en nmap:** Rechaza IPs en rango (e.g., `192.168.1.1-254`) pero permite hostnames con guión como `juice-shop` (corrección específica usando regex `\d+-\d+` en lugar de una comprobación genérica de guiones).

### 6.3 ZAP Scanner (`server/modules/zap_scanner.py`)

**Función:** Dynamic Application Security Testing (DAST) — spider y escaneo activo.

**Modo de operación:** La función unificada `run_zap_full()` combina el spider y el escaneo activo en un solo paso, eliminando el bug de "doble ejecución" de versiones anteriores donde ZAP era invocado dos veces separadamente con IDs de spider inválidos.

**Selección de política de escaneo por objetivo:**
| Target | Política ZAP |
|---|---|
| DVWA | `Dev Standard` |
| WebGoat | `Dev Standard` |
| Juice Shop | `Dev CICD` |
| Testfire | `Dev Full` |
| Genérico | `Default Policy` |

**Configuración del contenedor ZAP:**
```yaml
command: >
  zap.sh -daemon -host 0.0.0.0 -port 8080
  -config api.key=${ZAP_API_KEY}
  -config api.addrs.addr.name=.* -config api.addrs.addr.regex=true
  -config scanner.antiCSRF.tokenNames=csrf_token,_token,user_token
  -config spider.thread=5
  -config scanner.threadPerHost=3
```

**Límites de memoria:** `3G` límite, `512M` reserva, corriendo en la red `securescan-net` y `lab-net`.

**Inyección de URLs descubiertas:** Antes de ejecutar el escaneo activo ZAP, el orquestador inyecta las URLs descubiertas por ffuf y Gobuster en ZAP usando `inject_urls()`. Esto está protegido con `hasattr(orchestrator.zap, 'inject_urls')` para fallar silenciosamente si el método no existe en la versión de ZAP conectada.

**Salida esperada de `run_zap_full()`:**
```json
{
  "urls_descubiertas": ["http://target/login", "http://target/api/v1/users"],
  "vulnerabilidades": [
    {
      "name": "SQL Injection",
      "risk": "high",
      "url": "http://target/search?q=test",
      "description": "...",
      "solution": "...",
      "tool": "zap"
    }
  ],
  "tool": "zap_full",
  "success": true
}
```

### 6.4 Nuclei Scanner (`server/modules/nuclei.py`)

**Función:** Escaneo basado en plantillas de vulnerabilidades conocidas.

**Versión:** nuclei v3.2.4 (instalado como binario Go en el Dockerfile).

**Flag de salida:** `-jsonl` (una línea JSON por hallazgo). **Importante:** en versiones anteriores se usaba incorrectamente `-json`, lo cual solo funciona en versiones antiguas de Nuclei.

**Filtros de protocolo para reducir templates:**
```bash
nuclei -u <target> -jsonl -ept dns,ssl,tcp,whois,javascript
       -max-host-error 10 -fhr
       -tags <tags_segun_objetivo>
```

La opción `-ept` (exclude protocols) reduce el conjunto de ~12.841 templates a ~5.000 activos para el contexto web, consiguiendo una reducción del 60% en tiempo de carga.

**Templates por objetivo:**
| Objetivo | Tags utilizados |
|---|---|
| Juice Shop | `cve,sqli,xss,jwt,cors,ssrf,owasp,exposure,swagger,token,oauth,misconfig,header,redirect,api,nodejs` |
| DVWA | `cve,sqli,xss,lfi,rce,rfi,default-login,misconfig,header,php,exposure` |
| WebGoat | `cve,sqli,xss,jwt,xxe,ssrf,cors,misconfig,header,java,spring,exposure` |
| Genérico | `cve,exposure,misconfig,default-login,header,cors,ssrf,token,redirect` |

**Configuración de Nuclei en el Dockerfile:**
```dockerfile
RUN mkdir -p /home/scanner/.config/nuclei \
    && echo "nuclei-templates-directory: /home/scanner/nuclei-templates" \
       > /home/scanner/.config/nuclei/config.yaml \
    && chown -R scanner:scanner /home/scanner/.config \
    && chown -R scanner:scanner /home/scanner/nuclei-templates \
    && chmod -R 755 /home/scanner/.config
```

Esta configuración garantiza que el usuario `scanner` (no-root) pueda leer y escribir en el directorio de templates, corrigiendo los errores de permisos de versiones anteriores.

### 6.5 SQLMap Enterprise Scanner (`server/modules/sqlmap.py`)

**Función:** Detección y explotación controlada de SQL Injection.

**Modo de operación:** Usa la SQLMap REST API (`sqlmapapi.py`) en lugar de la CLI directa, lo que permite obtener resultados estructurados en JSON.

**Uso como context manager (obligatorio):**
```python
with SQLMapEnterpriseScanner(timeout=600, level=3, risk=2, threads=5) as scanner:
    results = run_with_timeout(
        scanner.scan, args=(target,),
        kwargs={'params': params, 'cookie': cookie, 'data': data},
        seconds=600,
    )
```

**Parámetros configurables via entorno:**
```
SQLMAP_LEVEL=3     # Nivel de tests (1-5)
SQLMAP_RISK=2      # Riesgo de payloads (1-3)
SQLMAP_THREADS=5   # Threads paralelos
```

**Selección inteligente de targets para DVWA:**
```python
# DVWA — URLs específicas de SQLi conocidas
for ep, param in [
    ('/vulnerabilities/sqli/?id=1&Submit=Submit', 'id'),
    ('/vulnerabilities/sqli_blind/?id=1&Submit=Submit', 'id'),
]:
```

**Corrección crítica:** El valor retornado por la SQLMap API para el campo `value` es un string Python que representa una estructura de datos. Debe procesarse con `ast.literal_eval()` en lugar de `json.loads()`. Adicionalmente, `wait_for_completion()` requiere un `sleep(2)` adicional tras recibir el estado `"terminated"`.

### 6.6 ffuf Scanner (`server/modules/ffuf.py`)

**Función:** Fuzzing de endpoints y descubrimiento de rutas/archivos.

**Versión:** ffuf v2.1.0 (Go binary).

**Comando base:**
```bash
ffuf -u <target>/FUZZ -w <wordlist> -o <output.json> -of json
     -H "Cookie: <cookie>" -mc 200,204,301,302,307,401,403
     -ac -t 10 -timeout 10
```

**Nota crítica:** La flag `-se` (stop on errors) fue eliminada en versiones anteriores porque hacía que ffuf terminase al primer error de red, antes de encontrar ningún resultado.

**Ruta de fuzzing para WebGoat:**
```python
fuzz_path = '/WebGoat/FUZZ' if ('webgoat' in t or '8080' in t) else '/FUZZ'
```

**Salida esperada:**
```json
[{
  "tool": "ffuf",
  "target": "http://localhost:3001",
  "endpoints": [
    {"url": "http://localhost:3001/api", "status": 200, "size": 1234, "words": 56},
    {"url": "http://localhost:3001/admin", "status": 403, "size": 89, "words": 3}
  ]
}]
```

### 6.7 Gobuster Enterprise Scanner (`server/modules/gobuster.py`)

**Función:** Enumeración avanzada de directorios y archivos.

**Versión:** gobuster v3.6.0 (Go binary). Se especifica esta versión porque v3.8.2 requiere la directiva `tool` de Go 1.24, incompatible con Go 1.22.5 instalado.

**Detección dinámica de wordlists:**
```python
# Cadena de fallback (FALLBACK_CHAIN)
1. /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt  (SecLists)
2. /app/wordlist-common.txt                                          (incluida en el repo)
3. /usr/share/wordlists/dirb/common.txt                             (enlace simbólico)
```

**Corrección clave:** `gobuster.scan()` no acepta parámetros `threads=` ni `delay=` en la llamada. Estos valores deben pasarse en `__init__()` al instanciar la clase.

```python
self.gobuster = GobusterScanner(
    threads=gobuster_threads,        # ← en __init__
    initial_delay_ms=gobuster_delay, # ← en __init__
    timeout=gobuster_timeout,        # ← en __init__
)
```

**Detección de tecnología para selección de wordlist:**
```python
class TechFingerprint(Enum):
    WORDPRESS = "wordpress"
    APACHE    = "apache"
    NODEJS    = "nodejs"
    PHP       = "php"
    JAVA      = "java"
    GENERIC   = "generic"
```

**Target especial para WebGoat:**
```python
gobuster_target = (
    f"{target.rstrip('/')}/WebGoat"
    if ('webgoat' in t or '8080' in t) else target
)
```

Esto es necesario porque WebGoat sirve toda su aplicación bajo el path `/WebGoat/`, y Gobuster necesita ese prefijo para encontrar recursos.

### 6.8 Metasploit Scanner (`server/modules/metasploit.py`)

**Función:** Selección inteligente y ejecución de módulos Metasploit via Console RPC.

**Librería:** `pymetasploit3` (con fallback a simulación si no está disponible).

**Módulos base siempre ejecutados:**
```python
_BASE_WEB = [
    ("auxiliary/scanner/http/http_version",  {"THREADS": 5}, "info",   30),
    ("auxiliary/scanner/http/options",        {"THREADS": 5}, "medium", 30),
    ("auxiliary/scanner/http/dir_listing",    {"THREADS": 5}, "medium", 45),
    ("auxiliary/scanner/http/robots_txt",     {},              "info",   30),
]
```

**Módulos por tecnología detectada:**
```python
_BY_TECH = {
    "apache tomcat": [
        ("auxiliary/scanner/http/tomcat_mgr_login", {"THREADS": 3, "STOP_ON_SUCCESS": True}, "critical", 120),
        ("auxiliary/scanner/http/tomcat_enum",       {"THREADS": 3}, "high", 60),
    ],
    # ... otros por tecnología
}
```

**Modo simulación:** Cuando `msfrpcd` no está disponible o la conexión RPC falla, el módulo retorna automáticamente resultados marcados con `"simulated": true` sin interrumpir el pipeline.

**Dependencia en docker-compose:** `api` depende de `msfrpcd` con `service_started` (no `service_healthy`) porque Metasploit puede tardar más de 5 minutos en arrancar, y no se debe bloquear la API mientras espera.

### 6.9 Searchsploit (`server/modules/searchsploit.py`)

**Función:** Búsqueda de exploits en la base de datos local ExploitDB.

**Instalación:** Repositorio ExploitDB clonado en `/opt/exploitdb` durante la construcción de la imagen Docker. El binario `searchsploit` es un enlace simbólico a `/opt/exploitdb/searchsploit`.

**Comando ejecutado:**
```bash
searchsploit --json <término>
```

La flag `--json` produce salida estructurada con todos los campos (ID, título, tipo, path local, CVE). Esto es más robusto que parsear la salida de texto plano.

**Rutas de búsqueda del repositorio:**
```python
_EXPLOITDB_PATHS = [
    '/opt/exploitdb',
    '/usr/share/exploitdb',
    os.path.expanduser('~/.local/share/exploitdb'),
]
```

**Salida enriquecida:**
```json
[{
  "id": "51337",
  "title": "Apache HTTP Server 2.4.49 - Path Traversal and RCE",
  "type": "remote",
  "cve": "CVE-2021-41773",
  "path": "/opt/exploitdb/exploits/webapps/51337.py",
  "url": "https://www.exploit-db.com/exploits/51337"
}]
```

### 6.10 Patator Scanner (`server/modules/patator.py`)

**Función:** Ataques de fuerza bruta y diccionario contra formularios de login HTTP.

**Estrategia en cascada:**
1. `requests` con manejo automático de CSRF token — compatible con DVWA, WebGoat, Juice Shop.
2. Binario `patator` como fallback si está disponible en PATH.
3. `_simulate_scan()` solo si ninguno está disponible.

**Wordlists integradas:**
```python
_DEFAULT_USERS = [
    'admin', 'guest', 'marlon', 'securescan',
    'admin@juice-sh.op',    # Juice Shop
    'jsmith',               # Testfire
    'administrator', 'user', 'test', 'root', 'demo',
    'operator', 'manager', 'support',
]

_DEFAULT_PASSES = [
    'password',             # DVWA: admin/password
    'admin123',             # Juice Shop: admin@juice-sh.op/admin123
    'Password',             # WebGoat: securescan/Password
    'demo1234',             # Testfire
    'admin', '123456', 'root', 'pass', 'guest', 'test',
]
```

**Captura de cookie de sesión:** La cookie se extrae de cualquier respuesta exitosa (código 200 ó 302 con redirección a URL distinta del login), no exclusivamente de redirects 302. Esto corrige falsos negativos en aplicaciones que retornan 200 con redirección JavaScript.

**Deduplicación de credenciales:** Se usa un set `seen_creds` para no reportar la misma combinación usuario/contraseña varias veces cuando múltiples intentos tienen éxito.

### 6.11 InjectionScanner (`server/modules/injection_scanner.py`)

**Función:** Motor interno de detección activa de 10 tipos de inyección.

Este es el módulo más extenso del proyecto (76.617 bytes), desarrollado específicamente para SecureScan Pro.

**Técnicas cubiertas:**

| # | Técnica | Subtipos |
|---|---|---|
| 1 | SQL Injection | Error-based, UNION, Boolean-Blind, Time-Blind, Auth-Bypass, Stacked, Second-Order |
| 2 | NoSQL Injection | MongoDB operators (`$gt`, `$ne`), regex bypass |
| 3 | XPath Injection | Auth bypass, error-based |
| 4 | XML / XXE | File read, OOB, blind |
| 5 | XSS | Reflected, Stored, DOM |
| 6 | Command Injection | OS command execution con semicolons, pipes, backticks |
| 7 | Path Traversal | LFI, directory escape (`../../../etc/passwd`) |
| 8 | SSRF | Acceso a hosts internos, bypass de CORS |
| 9 | SSTI | Evaluación de templates (Jinja2, Twig, Freemarker, etc.) |
| 10 | LDAP Injection | Filter bypass (`*)(uid=*))(|(uid=*` etc.) |

**Compatibilidad por laboratorio:**
- **Juice Shop:** REST API / JSON / JWT (Bearer token en cabeceras).
- **DVWA:** Formularios PHP / cookies de sesión (security=low obligatorio).
- **WebGoat:** Java Spring / JSON / JWT.
- **Genérico:** Detección básica en formularios HTML estándar.

**Fallback a SQLMap:** Si el módulo `InjectionScanner` no está instalado (importación fallida), el orquestador cae automáticamente en `run_sqlmap()` usando los targets identificados por `_get_sqlmap_targets()`.

---

## 7. UTILIDADES DEL BACKEND (server/utils/)

### 7.1 Sistema de Scoring (`server/utils/scoring.py`)

**Función:** Calcular la puntuación de seguridad global del objetivo analizado.

**Metodología:** Sistema de puntuación ponderada basado en CVSS-like:

```python
@dataclass
class SecurityWeights:
    critical: float = 20.0
    high:     float = 10.0
    medium:   float = 5.0
    low:      float = 2.0
    info:     float = 0.5
    exploit_with_vuln:    float = 8.0   # Penalización adicional si hay exploit para vuln
    exploit_without_vuln: float = 3.0   # Penalización si hay exploit relacionado
```

**Algoritmo:**
- Puntuación base: 100.
- Por cada vulnerabilidad de severidad X: resta `weights.X` puntos.
- Si existe un exploit correlacionado con una vulnerabilidad: resta `exploit_with_vuln` puntos adicionales.
- Exploits sin vulnerabilidad correlacionada: resta `exploit_without_vuln` puntos.
- La puntuación nunca puede ser negativa (clamped a 0).
- Las credenciales encontradas por Patator añaden penalización adicional como vulnerabilidad de tipo `brute_force`.

**Escala de calificaciones:**

| Rango | Grade | Risk Level | Descripción |
|---|---|---|---|
| 90-100 | A+ / A | LOW | Sin vulnerabilidades significativas |
| 80-89 | B+ / B | LOW | Vulnerabilidades bajas/informativas |
| 70-79 | C+ / C | MEDIUM | Vulnerabilidades medias detectadas |
| 60-69 | D+ / D | HIGH | Vulnerabilidades altas |
| 0-59 | F | CRITICAL | Vulnerabilidades críticas o exploits activos |

**Estructura de respuesta del scoring:**
```json
{
  "total": 65,
  "grade": "D+",
  "breakdown": {"critical": 0, "high": 2, "medium": 5, "low": 8, "info": 12},
  "riskLevel": "HIGH",
  "gradeDescription": "Security issues found — review recommended",
  "recommendations": ["Patch high vulnerabilities immediately", "..."],
  "exploitImpact": {"direct": 1, "indirect": 3},
  "metrics": {
    "total_vulns": 27,
    "max_cvss": 8.5,
    "exploitable": 4,
    "brute_force_success": false
  }
}
```

### 7.2 Generador de Reportes (`server/utils/reporter.py`)

**Función:** Generar reportes exportables en múltiples formatos.

**Formatos soportados:**

| Formato | Función | Librería | Notas |
|---|---|---|---|
| `html` | `generate_html_report()` | stdlib `html.escape()` | Report completo con estilos embebidos |
| `pdf` | `generate_pdf_report()` | `pdfkit` + `wkhtmltopdf` | Convierte el HTML a PDF |
| `json` | `generate_json_report()` | `json` stdlib | Datos completos sin formato |
| `csv` | `generate_csv_report()` | `csv` stdlib | Solo vulnerabilidades tabuladas |

**Sanitización XSS:** Todo el contenido insertado en el HTML es sanitizado con `html.escape(text, quote=True)` antes de ser renderizado.

**Secciones del reporte HTML:**
- Encabezado con metadata del scan (ID, target, tiempo de inicio/fin, estado)
- Panel de puntuación visual (grade, risk level, barras de conteo por severidad)
- Recomendaciones priorizadas (URGENT / HIGH / MEDIUM)
- Tabla de vulnerabilidades con CVSS, descripción y solución
- Tecnologías detectadas (Wappalyzer)
- Puertos abiertos (Nmap)
- Directorios/rutas descubiertas (Gobuster, ffuf)
- Hallazgos Metasploit
- Exploits correlacionados (Searchsploit)

**Almacenamiento de reportes:**
```
/app/reports/report-<scan_id>.<format>
```
(Mapeado al volumen Docker `scan-reports`).

---

## 8. FRONTEND — NEXT.JS / REACT

### 8.1 Stack tecnológico frontend

| Tecnología | Versión | Rol |
|---|---|---|
| Next.js | 14.2.5 | Framework React con App Router |
| React | 18.3.1 | Librería de UI |
| TypeScript | 5.4.x | Tipado estático |
| Tailwind CSS | 3.4.x | Framework de estilos utility-first |
| Shadcn/ui | (componentes) | Componentes accesibles sobre Radix UI |
| Radix UI | múltiple | Primitivos de UI accesibles sin estilo |
| TanStack Query | 5.28.x | Data fetching y cache de server state |
| React Hook Form | 7.51.x | Manejo de formularios |
| Zod | 3.22.x | Validación de schemas |
| Recharts | 2.12.x | Gráficos y visualizaciones |
| Lucide React | 0.400.x | Iconos SVG |
| date-fns | 3.6.x | Utilidades de fechas |
| react-day-picker | **8.10.1** | Selector de fechas (downgrade de v9 — API v8) |
| Sonner | 1.4.x | Notificaciones toast |
| pnpm | 8.15.0 | Package manager (requerido: ≥8) |
| Node.js | ≥20.0.0 | Runtime |

**Importante:** `react-day-picker` está fijado en v8.10.1. La versión v9 tiene una API incompatible que requería una reescritura completa de `components/ui/calendar.tsx`. La v8 usa `DayPicker` con props `mode`, `selected`, `onSelect`, `fromDate`, `toDate` directamente.

### 8.2 Estructura de la aplicación (App Router)

**`app/scanner/page.tsx`** — Página principal del escáner. Es el componente de mayor complejidad del frontend. Contiene:
- Panel de estadísticas por herramienta (`TOOL_META` con iconos por módulo).
- Grid de labs con URLs directas a los targets.
- Integración con `ScanProvider` (Context) para estado global del scan.
- Lógica de polling al endpoint `/api/scan/<id>/status`.

**`app/lab/page.tsx`** — Panel de control del laboratorio. Permite iniciar, detener y verificar el estado de los containers Docker (DVWA, Juice Shop, WebGoat) mediante los endpoints `/api/lab/<id>/start|stop|status`.

**`app/history/page.tsx`** — Historial de escaneos. Obtiene datos del endpoint `/api/history` y muestra los últimos 100 scans con estado, target, puntuación y acciones.

**`app/docs/page.tsx`** — Documentación embebida. Renderiza los archivos Markdown de `/public/docs/` a través de la API Route `app/api/docs/[slug]/route.ts`.

### 8.3 Componentes principales

**`components/scan-form.tsx`** — Formulario de inicio de escaneo con:
- Input de URL del target con validación en tiempo real.
- Selector rápido de labs (Juice Shop, DVWA, WebGoat) con un clic.
- Checkboxes para seleccionar herramientas (default: solo Wappalyzer + Nmap).
- Sección colapsable "Opciones avanzadas" con dry-run, circuit breaker y target validation.

**`components/scan-progress.tsx`** — Progreso en tiempo real:
- Lista de pasos del pipeline con iconos de estado (pending, running, completed, error).
- Barra de progreso global.
- Timer con ISO timestamp en UTC correcto.
- Polling automático cada 2 segundos al endpoint `/api/scan/<id>/status`.

**`components/results-dashboard.tsx`** — Dashboard de resultados (62 KB, el componente más grande):
- Tabs por categoría: Vulnerabilidades / Tecnologías / Puertos / Directorios / SQLi / Nuclei / Brute Force / Exploits / Metasploit.
- Filtros por severidad.
- Badges coloreados por nivel de riesgo.
- Visualizaciones con Recharts (distribución de vulnerabilidades por severidad).
- Acciones de exportación de reporte (abre `ReportDownloadModal`).

**`components/report-download-modal.tsx`** — Modal para descarga de reportes:
- Selector de formato (HTML, PDF, JSON, CSV).
- Descarga directa via `fetch()` con `blob()` y creación de URL temporal.

### 8.4 Cliente de API (`lib/api-client.ts`)

Centraliza toda la comunicación con el backend. Incluye:

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'
const API_TOKEN   = process.env.NEXT_PUBLIC_API_TOKEN || ''

// Interfaces tipadas completas
interface ScanStartRequest { target: string; options?: { tools?: {...}; dry_run?: boolean; ... } }
interface ScanStartResponse { jobId: string; status: 'running' | 'pending' }
interface ScanStep { name: string; status: 'pending'|'running'|'completed'|'error'; progress: number; ... }
interface SecurityScore { total: number; grade: Grade; breakdown: {...}; riskLevel: RiskLevel; ... }
interface ScanResults { id: string; target: string; status: string; steps: ScanStep[]; ... }
```

Funciones exportadas principales:
- `startScan(target, options)` → `POST /api/scan`
- `getScanResults(jobId)` → `GET /api/scan/<id>/status`
- `getScanHistory()` → `GET /api/history`
- `deleteScan(scanId)` → `DELETE /api/scan/<id>`
- `downloadReport(scanId, format)` → `GET /api/scan/<id>/report?format=<fmt>`
- `getLabStatus()` → `GET /api/lab/status`
- `startLab(labId)` → `POST /api/lab/<id>/start`
- `stopLab(labId)` → `POST /api/lab/<id>/stop`

### 8.5 Context de escaneo (`lib/scan-context.tsx`)

```typescript
// Estado global compartido entre componentes
interface ScanContextValue {
  currentScan: ScanResults | null
  isScanning: boolean
  error: string | null
  startScan: (target: string, options: ScanOptions) => Promise<void>
  cancelScan: () => void
  clearResults: () => void
}
```

El contexto maneja el ciclo completo: inicio del scan → polling de estado → finalización → error. Los componentes consumen el contexto con `useScan()`.

---

## 9. INFRAESTRUCTURA DOCKER Y DOCKER COMPOSE

### 9.1 Servicios definidos en docker-compose.yml

| Servicio | Container | Imagen | Puertos (host:container) | Red(es) |
|---|---|---|---|---|
| `frontend` | `securescan-frontend` | Build `Dockerfile.frontend` | `3000:3000` | `securescan-net` |
| `api` | `securescan-api` | Build `server/Dockerfile` | `5000:5000` | `securescan-net`, `lab-net` |
| `redis` | `securescan-redis` | `redis:7-alpine` | `127.0.0.1:6379:6379` | `securescan-net` |
| `zap` | `securescan-zap` | `ghcr.io/zaproxy/zaproxy:stable` | `8080:8080` | `securescan-net`, `lab-net` |
| `sqlmapapi` | `securescan-sqlmapapi` | Build `server/Dockerfile` | `127.0.0.1:8775:8775` | `securescan-net`, `lab-net` |
| `msfrpcd` | `securescan-msfrpcd` | `metasploitframework/metasploit-framework:latest` | `55553:55553` | `securescan-net`, `lab-net` |
| `juice-shop` | `juice-shop` | `bkimminich/juice-shop:v17.0.0` | `3001:3000` | `lab-net` |
| `dvwa` | `dvwa` | `ghcr.io/digininja/dvwa:latest` | `3002:80` | `lab-net` |
| `dvwa-db` | `dvwa-db` | `mariadb:10.11` | — (interno) | `lab-net` |
| `webgoat` | `webgoat` | `webgoat/webgoat:latest` | `3003:8080` | `lab-net` |

**Total: 10 servicios orquestados.**

### 9.2 Dockerfile del Backend (server/Dockerfile)

Base: `python:3.11-slim-bookworm` (Debian 12).

**Instalaciones en orden:**

1. **Paquetes APT base:** `nmap`, `patator`, `curl`, `wget`, `ca-certificates`, `git`, `unzip`, `nodejs`, `npm`, `python3`, `python3-pip`, `wkhtmltopdf`, `xvfb`, `libcap2-bin`.

2. **Go 1.22.5 (instalación manual):**
   ```dockerfile
   RUN curl -fsSL https://go.dev/dl/go1.22.5.linux-amd64.tar.gz | tar -C /usr/local -xz
   ENV PATH="/usr/local/go/bin:${GOPATH}/bin:..."
   ```
   El paquete `golang-go` de Debian Bookworm es la versión 1.19, incompatible con los módulos Go requeridos.

3. **SQLMap:** Clonado desde GitHub en `/opt/sqlmap`. Enlace simbólico a `/usr/local/bin/sqlmap`.

4. **Herramientas Go (versiones fijas):**
   ```dockerfile
   RUN go install github.com/OJ/gobuster/v3@v3.6.0 \
    && go install github.com/ffuf/ffuf/v2@v2.1.0 \
    && go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@v3.2.4
   ```

5. **SecLists:** Clonado en `/opt/SecLists` con enlace simbólico en `/usr/share/wordlists/seclists`.

6. **ExploitDB:** Clonado en `/opt/exploitdb` con enlace simbólico `searchsploit → /usr/local/bin/searchsploit`.

7. **Usuario no-root:** `scanner:scanner` — el backend corre con este usuario en producción.

8. **Capacidades nmap:**
   ```dockerfile
   RUN setcap cap_net_raw,cap_net_admin+eip /usr/bin/nmap || true
   ```

9. **Templates Nuclei:** Clonados en `/home/scanner/nuclei-templates`, con configuración de permisos correcta.

10. **Gunicorn:**
    ```dockerfile
    CMD ["sh", "-c", "gunicorn \
        --bind 0.0.0.0:5000 \
        --workers 2 \
        --threads 4 \
        --worker-class sync \
        --worker-tmp-dir /dev/shm \
        --timeout ${GUNICORN_TIMEOUT:-3600} \
        --graceful-timeout 30 \
        app:app"]
    ```

### 9.3 Dockerfile del Frontend (Dockerfile.frontend)

Base: `node:20-alpine`. Usa el patrón multi-stage build:
- **Stage `deps`:** Instala dependencias con pnpm.
- **Stage `builder`:** Construye la aplicación Next.js con `pnpm build`.
- **Stage `runner`:** Solo el output de Next.js standalone, sin fuentes ni devDependencies.

### 9.4 Volúmenes persistentes

| Volumen | Uso |
|---|---|
| `redis-data` | Datos persistentes de Redis |
| `scan-reports` | Reportes generados (HTML, PDF, JSON, CSV) |
| `dvwa-db-data` | Base de datos MariaDB de DVWA |
| `msf-data` | Configuración y base de datos de Metasploit |
| `nuclei-templates` | Templates de Nuclei (se actualiza automáticamente) |
| `juice-shop-data` | Datos de OWASP Juice Shop |
| `webgoat-data` | Datos de WebGoat |

### 9.5 Health Checks

Todos los servicios críticos tienen health checks:

```yaml
# Redis
test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
interval: 10s

# API Flask
test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
interval: 30s, start_period: 30s, retries: 5

# ZAP
test: ["CMD", "curl", "-f", "http://localhost:8080/JSON/core/view/version/?apikey=${ZAP_API_KEY}"]
interval: 30s, start_period: 60s, retries: 5

# DVWA
test: ["CMD", "curl", "-f", "http://localhost:80"]
interval: 30s, start_period: 45s, retries: 5
```

---

## 10. PIPELINE DE ESCANEO — FLUJO COMPLETO DE 11 PASOS

```
INICIO
  │
  ▼
[Auto-login]  _get_session_for_target(target) → session_cookie
  │
  ├─ Paso 1 ─ Wappalyzer
  │           └─ Identifica tecnologías → technologies[]
  │
  ├─ Paso 2 ─ Nmap
  │           └─ Escanea puertos → ports[]
  │
  ├─ Paso 3 ─ Patator       ← Cookie disponible para pasos 4-10
  │           └─ Fuerza bruta → brute_force_results[]
  │           └─ (extrae session_cookie si encuentra credenciales)
  │
  ├─ Paso 4 ─ Metasploit
  │           └─ Módulos RPC → msf_results[]
  │
  ├─ Paso 5 ─ ffuf
  │           └─ Fuzzing endpoints → ffuf_endpoints[]
  │
  ├─ Paso 6 ─ Gobuster
  │           └─ Dir enumeration → directories[]
  │
  ├─ Paso 7 ─ ZAP Full Scan  (Spider + Active Scan unificados)
  │           ├─ Inyecta URLs de ffuf y Gobuster en ZAP
  │           └─ → spider_results[] + vulnerabilities[]
  │
  ├─ Paso 8 ─ Nuclei
  │           └─ Template scan → nuclei_findings[]
  │
  ├─ Paso 9 ─ InjectionScanner (10 técnicas) / SQLMap fallback
  │           └─ → sqli_results[]
  │
  ├─ Paso 10 ─ Searchsploit
  │            └─ Correlaciona technologies + ports → exploits[]
  │
  └─ Paso 11 ─ Scoring
               └─ calculate_security_score() → score{}
                  {total, grade, breakdown, riskLevel, recommendations}
```

**Persistencia en cada paso:**

En `app.py`, tras cada paso exitoso, el resultado se persiste inmediatamente en Redis mediante `_persist_step_result()`:

```python
def _persist_step_result(job_id: str, field: str, value) -> None:
    fresh = get_scan(job_id)  # Lee estado actual de Redis
    if fresh:
        fresh[field] = value
        save_scan(job_id, fresh)
```

Esto garantiza que si el proceso muere a mitad del pipeline, los resultados parciales no se pierden.

**Estado final del objeto scan en Redis:**
```json
{
  "id": "uuid-v4",
  "target": "http://juice-shop:3000",
  "status": "completed",
  "startTime": "2026-06-05T10:00:00Z",
  "endTime": "2026-06-05T10:35:00Z",
  "steps": [ {"name": "Wappalyzer", "status": "completed", "progress": 100}, ... ],
  "technologies": [...],
  "ports": [...],
  "directories": [...],
  "spider_results": [...],
  "vulnerabilities": [...],
  "exploits": [...],
  "metasploit": [...],
  "nuclei_findings": [...],
  "sqli_results": [...],
  "brute_force_results": [...],
  "ffuf_endpoints": [...],
  "score": { "total": 72, "grade": "C", "breakdown": {...}, "riskLevel": "MEDIUM" }
}
```

---

## 11. API REST — REFERENCIA DE ENDPOINTS

### 11.1 Health Check

```
GET /api/health
Autenticación: No requerida
Rate limit: Exento
```

**Respuesta:**
```json
{
  "status": "healthy",
  "version": "5.0.0",
  "storage": "connected",
  "zap_configured": true,
  "tools": ["wappalyzer", "nmap", "gobuster", "zap", "searchsploit",
            "metasploit", "nuclei", "sqlmap", "injection_scanner", "patator", "ffuf"]
}
```

### 11.2 Iniciar Escaneo

```
POST /api/scan
Content-Type: application/json
X-API-Token: <token>
Rate limit: 20/hora
```

**Request body:**
```json
{
  "target": "http://juice-shop:3000",
  "options": {
    "tools": {
      "wappalyzer": true,
      "nmap": true,
      "gobuster": true,
      "zap": true,
      "searchsploit": true,
      "metasploit": false,
      "nuclei": true,
      "sqlmap": true,
      "patator": true,
      "ffuf": true
    },
    "dry_run": false,
    "circuit_breaker": {
      "enabled": true,
      "failure_threshold": 3,
      "recovery_timeout": 60
    },
    "target_validation": {
      "check_dns": true,
      "check_reachability": true,
      "timeout": 10
    },
    "retry_config": {
      "max_retries": 1,
      "backoff_factor": 1.5,
      "retry_on": ["timeout", "connection_error"]
    }
  }
}
```

**Respuesta exitosa (202):**
```json
{"jobId": "550e8400-e29b-41d4-a716-446655440000", "status": "running"}
```

**Respuesta dry-run (200):**
```json
{"jobId": "...", "status": "completed", "dry_run": true}
```

**Errores posibles:**
- `400` — JSON inválido o target vacío.
- `403` — Target no permitido (en modo `RESTRICT_TO_LAB_TARGETS=true`).
- `422` — Target no alcanzable (DNS o TCP).
- `429` — Circuit breaker abierto para ese target.
- `401` — Token inválido.

### 11.3 Estado del Escaneo

```
GET /api/scan/<scan_id>/status
X-API-Token: <token>
Rate limit: Exento
```

Devuelve el objeto scan completo con todos los resultados parciales y finales. Los campos de resultados se van rellenando a medida que avanzan los pasos.

### 11.4 Descargar Reporte

```
GET /api/scan/<scan_id>/report?format=<fmt>
X-API-Token: <token>
Rate limit: Exento
```

Formatos: `html`, `pdf`, `json`, `csv`.

Responde con `Content-Disposition: attachment; filename=security-report-<scan_id>.<fmt>`.

Solo disponible cuando el scan tiene `"status": "completed"`.

### 11.5 Historial de Escaneos

```
GET /api/history
X-API-Token: <token>
```

**Respuesta:**
```json
{
  "scans": [ ...últimos 100 objetos scan ordenados por startTime DESC... ],
  "total": 42
}
```

### 11.6 Eliminar Escaneo

```
DELETE /api/scan/<scan_id>
X-API-Token: <token>
```

Elimina el scan de Redis (o del fallback en memoria). Responde `200` con mensaje de confirmación.

### 11.7 Configuración del Sistema

```
GET /api/config
```

```json
{
  "version": "5.0.0",
  "allowed_targets": ["juice-shop:3000", "dvwa:80", "webgoat:8080"],
  "restrict_to_lab": false,
  "available_tools": ["wappalyzer", "nmap", "gobuster", "zap", ...],
  "report_formats": ["html", "json", "pdf", "csv"],
  "metasploit": {
    "enabled": true,
    "mode": "simulation",
    "host": "msfrpcd",
    "port": 55553
  }
}
```

### 11.8 Endpoints de Laboratorio

```
GET  /api/lab/status           → Estado de los 3 containers del lab
POST /api/lab/<id>/start       → Iniciar container (juice-shop | dvwa | webgoat)
POST /api/lab/<id>/stop        → Detener container
```

Estos endpoints interactúan con el socket Docker (`/var/run/docker.sock` montado en el container API). Los containers disponibles son: `juice-shop`, `dvwa`, `webgoat`.

---

## 12. VARIABLES DE ENTORNO Y CONFIGURACIÓN

Todas las variables se definen en `.env` (copiado desde `.env.example`).

### 12.1 Variables principales

| Variable | Default | Descripción |
|---|---|---|
| `SECRET_KEY` | *(requerido en prod)* | Clave secreta Flask. Generar con `openssl rand -hex 32` |
| `FLASK_ENV` | `development` | Modo Flask (`development` / `production`) |
| `PORT` | `5000` | Puerto del backend |
| `REDIS_URL` | `redis://:changeme-redis-password@redis:6379/0` | URL de conexión Redis |
| `REDIS_PASSWORD` | `changeme-redis-password` | Contraseña Redis |
| `ZAP_API_URL` | `http://zap:8080` | URL del servicio ZAP |
| `ZAP_API_KEY` | `securescan-dev-key-2024` | Clave API de ZAP |
| `MSF_HOST` | `msfrpcd` | Host del daemon Metasploit |
| `MSF_PORT` | `55553` | Puerto RPC de Metasploit |
| `MSF_PASSWORD` | `msf` | Contraseña RPC de Metasploit |
| `API_TOKEN` | *(vacío)* | Token de autenticación API. Si está vacío, no requiere autenticación |
| `ALLOWED_ORIGINS` | `http://localhost:3000,...` | Orígenes CORS permitidos |
| `ALLOWED_LAB_TARGETS` | `juice-shop:3000,dvwa:80,webgoat:8080` | Targets del laboratorio |
| `RESTRICT_TO_LAB_TARGETS` | `false` | Si `true`, solo permite targets del lab |
| `GUNICORN_TIMEOUT` | `3600` | Timeout de Gunicorn en segundos |

### 12.2 Timeouts por herramienta (segundos)

| Variable | Default |
|---|---|
| `SCAN_TIMEOUT_WAPPALYZER` | 60 |
| `SCAN_TIMEOUT_NMAP` | 300 |
| `SCAN_TIMEOUT_FFUF` | 300 |
| `SCAN_TIMEOUT_GOBUSTER` | 300 |
| `SCAN_TIMEOUT_ZAP` | 1200 |
| `SCAN_TIMEOUT_NUCLEI` | 1200 |
| `SCAN_TIMEOUT_SQLMAP` | 600 |
| `SCAN_TIMEOUT_PATATOR` | 180 |
| `SCAN_TIMEOUT_METASPLOIT` | 900 |
| `SCAN_TIMEOUT_SEARCHSPLOIT` | 120 |
| `SCAN_TIMEOUT_INJECTION` | 600 |

### 12.3 Parámetros de herramientas

| Variable | Default | Descripción |
|---|---|---|
| `SQLMAP_LEVEL` | 3 | Nivel de profundidad SQLMap (1-5) |
| `SQLMAP_RISK` | 2 | Riesgo de payloads SQLMap (1-3) |
| `SQLMAP_THREADS` | 5 | Threads paralelos SQLMap |
| `GOBUSTER_THREADS` | 20 | Threads paralelos Gobuster |
| `GOBUSTER_DELAY_MS` | 0 | Delay entre requests Gobuster (ms) |
| `ZAP_SPIDER_MAX_CHILDREN` | 50 | Máximo de URLs hijas en el spider ZAP |

### 12.4 Variables frontend (Next.js)

| Variable | Default | Descripción |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:5000` | URL base de la API para el cliente |
| `NEXT_PUBLIC_API_TOKEN` | *(vacío)* | Token de autenticación para el cliente |

---

## 13. LABORATORIO DE SEGURIDAD — TARGETS VULNERABLES

### 13.1 OWASP Juice Shop v17.0.0

**Container:** `juice-shop` | **Puerto local:** `3001` | **Red interna:** `juice-shop:3000`

Aplicación Node.js/Koa con SQLite que simula una tienda en línea con vulnerabilidades OWASP Top 10 2021 deliberadamente introducidas.

**Vulnerabilidades cubiertas:**
- A01: Broken Access Control (acceso directo a rutas de administración)
- A02: Cryptographic Failures (contraseñas débiles, JWT sin verificación)
- A03: Injection (SQLi en búsqueda de productos, XSS en comentarios)
- A07: Identification and Authentication Failures (brute force, tokens predecibles)
- A09: Security Logging and Monitoring Failures

**Credenciales de lab:** `admin@juice-sh.op` / `admin123` (auto-login configurado)

**API REST:** Juice Shop expone endpoints REST en `/rest/` y GraphQL en `/api/`. El auto-login usa `POST /rest/user/login` con JSON y obtiene un JWT válido.

### 13.2 DVWA (Damn Vulnerable Web Application)

**Container:** `dvwa` | **Puerto local:** `3002` | **Base de datos:** MariaDB 10.11 (`dvwa-db`)

Aplicación PHP clásica con vulnerabilidades categorizadas por nivel de dificultad (low / medium / high / impossible).

**Credenciales:** `admin` / `password` (auto-login configurado)

**Nivel de seguridad:** SecureScan Pro fuerza el nivel a `low` en el cookie `security=low` después del login, garantizando que todos los módulos (SQLMap, Nuclei) puedan explotar las vulnerabilidades sin restricciones adicionales del PHP de DVWA.

**Corrección DVWA crítica:** El cambio de nivel vía `POST /security.php` requiere un token CSRF propio de esa página, diferente al token del login. Sin este token, DVWA mantiene el nivel `impossible` silenciosamente.

**Módulos vulnerables más relevantes:**
- `/vulnerabilities/sqli/` — SQLi básica con parámetro `id`
- `/vulnerabilities/sqli_blind/` — SQLi ciega
- `/vulnerabilities/xss_r/` — XSS reflejado
- `/vulnerabilities/xss_s/` — XSS almacenado
- `/vulnerabilities/brute/` — Login con brute force
- `/vulnerabilities/upload/` — File upload sin validación

### 13.3 WebGoat

**Container:** `webgoat` | **Puerto local:** `3003` | **Puerto interno:** `8080`

Aplicación Java Spring Boot con lecciones interactivas de seguridad.

**Credenciales:** `securescan` / `Password` (auto-login configurado)

**Particularidades técnicas:**
- Requiere GET inicial antes del POST de login (Spring Security CSRF).
- Toda la aplicación está bajo el path `/WebGoat/`.
- El User-Agent del auto-login se propaga también a ZAP para coherencia.
- ffuf fuzzea bajo `/WebGoat/FUZZ` en lugar de `/FUZZ`.
- Gobuster usa `<target>/WebGoat` como raíz de enumeración.

---

## 14. SISTEMA DE PUNTUACIÓN DE SEGURIDAD

### 14.1 Algoritmo de cálculo

```python
# Pseudocódigo del algoritmo
score = 100.0

for vuln in vulnerabilities:
    severity = vuln.get('risk', 'info').lower()
    deduction = weights[severity]  # 20/10/5/2/0.5
    
    # Si hay exploit correlacionado: penalización adicional
    if has_matching_exploit(vuln, exploits):
        deduction += weights.exploit_with_vuln   # +8.0
    
    score -= deduction

# Exploits sin vulnerabilidad correlacionada
for exploit in orphan_exploits:
    score -= weights.exploit_without_vuln  # 3.0

# Brute force exitoso añade como vulnerabilidad alta
if any(bf.get('success') for bf in brute_force_results):
    score -= weights.high  # 10.0

# Clamp: mínimo 0, máximo 100
score = max(0.0, min(100.0, score))
```

### 14.2 Escala de calificación

| Score | Grade | Risk Level |
|---|---|---|
| 95-100 | A+ | LOW |
| 90-94 | A | LOW |
| 85-89 | A- | LOW |
| 80-84 | B+ | LOW |
| 75-79 | B | LOW |
| 70-74 | B- | MEDIUM |
| 65-69 | C+ | MEDIUM |
| 60-64 | C | MEDIUM |
| 55-59 | C- | MEDIUM |
| 50-54 | D+ | HIGH |
| 45-49 | D | HIGH |
| 40-44 | D- | HIGH |
| 0-39 | F | CRITICAL |

---

## 15. GENERACIÓN DE REPORTES

### 15.1 Formatos disponibles

**HTML:** Reporte completo con estilos CSS embebidos, secciones colapsables por categoría, badges de severidad coloreados y tabla de vulnerabilidades ordenada por riesgo. Usa `html.escape()` para prevenir XSS en el propio reporte.

**PDF:** Generado a partir del HTML usando `pdfkit` + `wkhtmltopdf`. `wkhtmltopdf` se instala explícitamente en el Dockerfile (requería `apt-get install wkhtmltopdf xvfb` — sin `xvfb` falla en entornos sin display).

**JSON:** Dump completo del objeto scan sin transformaciones. Útil para procesamiento automatizado o integración con otras herramientas.

**CSV:** Solo la tabla de vulnerabilidades, con columnas: `name, risk, url, description, solution, tool, cve`. Útil para importar en hojas de cálculo o sistemas de ticketing.

### 15.2 Ubicación de archivos

Los reportes se almacenan en el volumen `scan-reports` montado en `/app/reports/`:
```
/app/reports/report-550e8400-e29b-41d4-a716-446655440000.html
/app/reports/report-550e8400-e29b-41d4-a716-446655440000.pdf
/app/reports/report-550e8400-e29b-41d4-a716-446655440000.json
/app/reports/report-550e8400-e29b-41d4-a716-446655440000.csv
```

---

## 16. MECANISMOS DE RESILIENCIA Y SEGURIDAD

### 16.1 Circuit Breaker (doble capa)

**Capa 1 — app.py:** Verifica el estado del circuito antes de lanzar el thread de escaneo. Si el circuito está abierto para ese target, devuelve `429 Too Many Requests` inmediatamente.

**Capa 2 — orchestrator.py:** El orquestador tiene su propio circuit breaker interno que se consulta en `run_full_scan()`. Permite un control más granular por herramienta.

**Estado del circuito:**
- `closed` (normal): El sistema opera normalmente.
- `open` (fallo): Después de `failure_threshold` fallos, el circuito se abre y rechaza peticiones durante `recovery_timeout` segundos.
- `half-open` (recuperación): Tras el timeout, permite un intento. Si tiene éxito, vuelve a `closed`; si falla, vuelve a `open`.

### 16.2 Validación de targets (multi-nivel)

1. **Caracteres inválidos:** Rechaza targets con `@`, espacios, backslashes o newlines.
2. **Patrones de IPs privadas/loopback:** 7 patrones regex para IPv4 y 3 para IPv6.
3. **Lista de allowlist de laboratorio:** Los hostnames del lab siempre pasan.
4. **Modo restrictivo:** Si `RESTRICT_TO_LAB_TARGETS=true`, solo se permiten exactamente los targets del lab.
5. **Validación de alcanzabilidad:** DNS resolution + TCP connect (configurable por petición).

### 16.3 Aislamiento de red

Los containers del laboratorio solo tienen acceso a la red `lab-net`. La red `securescan-net` contiene los servicios de infraestructura (API, Redis, ZAP, Metasploit). La API tiene acceso a ambas redes para poder escanear los labs.

Redis solo acepta conexiones desde `127.0.0.1` (el puerto está mapeado como `127.0.0.1:6379:6379`, no `0.0.0.0:6379:6379`).

### 16.4 Seguridad del container API

```yaml
cap_add:
  - NET_RAW    # Para nmap (escaneo raw de sockets)
  - NET_ADMIN  # Para nmap (manipulación de interfaces)
security_opt:
  - no-new-privileges:true  # Previene escalada de privilegios
group_add:
  - "132"      # Grupo docker (para acceder al socket)
```

---

## 17. SCRIPTS DE AUTOMATIZACIÓN

### 17.1 start.sh — Arranque completo

Script de bash que automatiza el arranque completo de la plataforma en el orden correcto:

1. Verifica prerequisitos (Docker, Docker Compose v2).
2. Crea `.env` desde `.env.example` si no existe.
3. Construye las imágenes `api`, `sqlmapapi` y `frontend`.
4. Arranca Redis y espera a que responda con PONG.
5. Arranca ZAP en background.
6. Arranca los labs: primero `dvwa-db`, después DVWA, WebGoat y Juice Shop.
7. Arranca Metasploit en background.
8. Arranca el backend API y `sqlmapapi`, después el frontend.
9. Polling de `/api/health` hasta que responde (máximo 60s).
10. Muestra resumen con URLs y comandos útiles.

**Uso:**
```bash
chmod +x start.sh
bash start.sh
```

### 17.2 verify.sh — Verificación de estado

Comprueba el estado de todos los servicios, endpoints y herramientas instaladas. Útil para diagnóstico post-arranque.

### 17.3 fix_frontend_dvwa.sh — Corrección DVWA

Script específico que resuelve problemas de configuración del frontend con DVWA en ciertos entornos de laboratorio.

---

## 18. DEPENDENCIAS Y STACK TECNOLÓGICO COMPLETO

### 18.1 Python Backend (`server/requirements.txt`)

```
flask>=3.0.0,<4.0.0
flask-cors>=4.0.0,<5.0.0
flask-limiter>=3.5.0,<4.0.0
requests>=2.31.0,<3.0.0
redis>=5.0.0,<6.0.0
pdfkit>=1.0.0,<2.0.0
pymetasploit3>=1.0.3
python-Wappalyzer>=0.3.1
python-dotenv>=1.0.0,<2.0.0
pydantic>=2.0.0,<3.0.0
jinja2>=3.1.0,<4.0.0
docker>=7.1.0
beautifulsoup4>=4.12.0
gunicorn>=21.2.0
```

Instalados adicionalmente en el Dockerfile: `gevent` (workers async opcionales).

### 18.2 Herramientas del sistema (instaladas en la imagen Docker)

| Herramienta | Versión | Instalación |
|---|---|---|
| Python | 3.11 | Imagen base |
| Go | 1.22.5 | Instalación manual (`go.dev/dl`) |
| Nmap | APT | `apt-get install nmap` |
| Patator | APT | `apt-get install patator` |
| SQLMap | Git | `git clone https://github.com/sqlmapproject/sqlmap` |
| Gobuster | Go | `go install github.com/OJ/gobuster/v3@v3.6.0` |
| ffuf | Go | `go install github.com/ffuf/ffuf/v2@v2.1.0` |
| Nuclei | Go | `go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@v3.2.4` |
| Searchsploit | Git | `git clone https://gitlab.com/exploit-database/exploitdb` |
| wkhtmltopdf | APT | `apt-get install wkhtmltopdf xvfb` |
| SecLists | Git | `git clone https://github.com/danielmiessler/SecLists` |
| Nuclei-templates | Git | `git clone https://github.com/projectdiscovery/nuclei-templates` |

### 18.3 Imágenes Docker de terceros

| Imagen | Versión | Servicio |
|---|---|---|
| `python:3.11-slim-bookworm` | 3.11 slim | Base backend |
| `node:20-alpine` | 20 LTS | Base frontend |
| `redis:7-alpine` | 7 | Redis |
| `ghcr.io/zaproxy/zaproxy:stable` | stable | OWASP ZAP |
| `metasploitframework/metasploit-framework:latest` | latest | Metasploit |
| `bkimminich/juice-shop:v17.0.0` | 17.0.0 | OWASP Juice Shop |
| `ghcr.io/digininja/dvwa:latest` | latest | DVWA |
| `mariadb:10.11` | 10.11 | Base de datos DVWA |
| `webgoat/webgoat:latest` | latest | WebGoat |

### 18.4 Node.js Frontend (`package.json`)

Framework y librerías principales:
```json
{
  "next": "14.2.5",
  "react": "^18.3.1",
  "typescript": "^5.4.0",
  "tailwindcss": "^3.4.17",
  "@tanstack/react-query": "^5.28.0",
  "react-hook-form": "^7.51.0",
  "zod": "^3.22.0",
  "recharts": "^2.12.0",
  "lucide-react": "^0.400.0",
  "react-day-picker": "^8.10.1",
  "sonner": "^1.4.0",
  "pnpm": "8.15.0"
}
```

---

## 19. CORRECCIONES ACUMULADAS v5.0 — REGISTRO TÉCNICO

Este registro documenta todas las correcciones críticas aplicadas a lo largo del desarrollo del proyecto, relevantes para entender las decisiones de diseño actuales.

### 19.1 Backend (app.py)

| # | Corrección | Impacto |
|---|---|---|
| 1 | Race condition en `run_scan()` — resultados persistidos en Redis inmediatamente tras cada herramienta | Datos no se pierden si el proceso muere a mitad del scan |
| 2 | CORS lee orígenes desde variable de entorno `ALLOWED_ORIGINS` | Configurable sin recompilación |
| 3 | `get_scan_storage()` cachea estado de conexión 10s | Evita ping a Redis en cada operación |
| 4 | `scans_fallback` usa `threading.Lock` | Acceso seguro multi-hilo al diccionario en memoria |
| 5 | `FORBIDDEN_PATTERNS` — eliminada excepción inconsistente en `10.x.x.x` | Validación uniforme de IPs privadas |
| 6 | `request.get_json(silent=True)` | Sin crash con body malformado |
| 7 | `SECRET_KEY` con validación estricta en producción | Previene despliegue con clave débil |
| 8 | Autenticación por token `X-API-Token` en endpoints sensibles | Protección de la API |
| 9 | Rate limiting con `flask-limiter` | Previene abuso |
| 10 | Validación de `scan_id` como UUID v4 | Previene inyección en keys de Redis |
| 11 | `RESTRICT_TO_LAB_TARGETS` leída desde variable de entorno | Configurable por despliegue |
| 12 | ZAP unificado en `run_zap_full()` | Elimina doble ejecución y bug de Spider ID 0 |
| 13 | Numeración de pasos corregida en `run_scan()` | Sin duplicados |
| 14 | Patator en Paso 3 — antes de Nuclei (Paso 8) | Cookie disponible para herramientas posteriores |
| 15 | `scans_fallback` limitado a 200 entradas | Previene OOM sin Redis |
| 16 | Thread de escaneo `daemon=False` | Sobrevive al reciclaje de workers de Gunicorn |
| 17 | Paso 9 integra `run_injection_scan()` (10 técnicas) | Análisis de inyección más completo |
| 18 | `inject_urls` protegido con `hasattr()` en el paso de ZAP | Falla silenciosamente si método no existe |
| 19 | Campo renombrado: `nuclei_findings` (antes: `nikto_findings`) | Coherencia con el módulo real |
| 20 | `_persist_step_result()` lee estado fresco de Redis antes de escribir | Evita sobreescribir resultados parciales |

### 19.2 Orquestador (orchestrator.py)

| # | Corrección | Impacto |
|---|---|---|
| 1 | `run_nuclei()` — firma corregida: `dry_run=False, cookie=None` | Antes: `technologies` era interpretado como `dry_run=True` |
| 2 | `run_zap()` no existe → reemplazado por `run_zap_full()` | Error de nombre de método |
| 3 | Indentación rota en `__init__` | `self.searchsploit` era inalcanzable |
| 4 | Typo en WebGoat auto-login: `'securesacan'` → `'securescan'` | Login siempre fallaba para WebGoat |
| 5 | Patator movido a Fase 3 (antes Fase 9) | Nuclei y SQLMap necesitan la cookie |
| 6 | `zap.inject_urls()` protegido con `hasattr()` | Falla silenciosamente si método no existe |
| 7 | DVWA — `security.php` requiere su propio CSRF token | Sin token, DVWA mantiene nivel `impossible` |
| 8 | `nikto_findings` renombrado a `nuclei_findings` en results dict | Coherencia con módulo real |
| 9 | `_SKIP_EXPLOIT_TERMS` — eliminados términos útiles (`php`, `apache`, `nginx`, `sql`) | Searchsploit encontraba 0 exploits antes |
| 10 | `threading.Event` para timeouts seguros | `signal.SIGALRM` no funciona en threads |

### 19.3 Módulos individuales

| Módulo | Corrección |
|---|---|
| `gobuster.py` | `shutil.which()` en lugar de path hardcodeado; `__enter__`/`__exit__` duplicados eliminados |
| `ffuf.py` | Flag `-se` eliminada (abortaba al primer error de red) |
| `sqlmap.py` | `ast.literal_eval()` en lugar de `json.loads()` para el campo `value`; `sleep(2)` tras estado `terminated` |
| `patator.py` | `_brute_force_with_json()` para Juice Shop JWT; deduplicación con `seen_creds` |
| `nuclei.py` | Flag `-jsonl` en lugar de `-json` (v3.2.4); filtro `-ept dns,ssl,tcp,whois,javascript` |
| `nmap_scanner.py` | Regex `\d+-\d+` para detectar rangos IP sin rechazar hostnames con guión |
| `wappalyzer.py` | Fallback triple: librería Python → CLI → simulación |
| `metasploit.py` | Console RPC en lugar de API directa; modo simulación automático si msfrpcd no disponible |
| `searchsploit.py` | Flag `--json` para salida estructurada; `_SKIP_TERMS` corregido |

### 19.4 Dockerfile

| Corrección | Detalle |
|---|---|
| `wkhtmltopdf` + `xvfb` | Requerido por pdfkit para generar PDFs en entornos sin display |
| Go 1.22.5 manual | `golang-go` de Bookworm es 1.19, incompatible con los módulos Go requeridos |
| `chown` en nuclei-templates | Corrección de errores de permisos del usuario no-root |
| `setcap` en nmap | Permite escaneos raw sin ejecutar como root |
| `gevent` y `gunicorn` | Workers async para escaneos concurrentes |
| `GUNICORN_TIMEOUT` | Variable de entorno para timeouts de escaneos largos |

### 19.5 Frontend

| Corrección | Detalle |
|---|---|
| `react-day-picker@8.10.1` | Downgrade de v9 (API incompatible) a v8.10.1 |
| `calendar.tsx` reescrito | API v8: `DayPicker` con props `mode`, `selected`, `onSelect` |
| `api-client.ts` — tipos completos | `SecurityScore`, `Grade`, `RiskLevel` con todos los campos del backend |
| Campo `nuclei_findings` | Antes buscaba `nikto_findings` — actualizado al nombre correcto |

---

*Documento generado a partir del código fuente real de SecureScan Pro v5.0.*  
*Versión del sistema: `server/app.py` → v5.0.0, `orchestrator.py` → v5.0, `Dockerfile` → v3.1.3*  
*SENA — Programa Técnico en Seguridad de Aplicaciones Web — Colombia, 2026*
