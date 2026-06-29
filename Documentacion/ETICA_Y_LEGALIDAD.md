# ÉTICA Y LEGALIDAD EN EL USO DE SECURESCAN PRO
## Marco Ético, Legal y de Uso Responsable

**Proyecto:** SecureScan Pro v3.0 — Plataforma Automatizada de Análisis de Seguridad Web  
**Autor:** Tecnico en Seguridad de Aplicaciones Web  
**Institución:** SENA — Servicio Nacional de Aprendizaje (Colombia)  
**Programa:** Técnico en Seguridad de Aplicaciones Web  
**Fecha de actualización:** Junio 2026  

---

## TABLA DE CONTENIDOS

1. [Declaración de Principios Éticos](#1-declaración-de-principios-éticos)
2. [Marco Legal en Colombia](#2-marco-legal-en-colombia)
3. [Marco Legal Internacional de Referencia](#3-marco-legal-internacional-de-referencia)
4. [Controles Técnicos de Seguridad Ética Implementados en el Código](#4-controles-técnicos-de-seguridad-ética-implementados-en-el-código)
5. [Uso Autorizado y Uso No Autorizado](#5-uso-autorizado-y-uso-no-autorizado)
6. [Los Tres Laboratorios — Por Qué Son Legales y Seguros](#6-los-tres-laboratorios--por-qué-son-legales-y-seguros)
7. [Metasploit en Modo Auxiliar — Distinción Técnica y Ética](#7-metasploit-en-modo-auxiliar--distinción-técnica-y-ética)
8. [Responsabilidades del Operador](#8-responsabilidades-del-operador)
9. [Privacidad y Protección de Datos de los Reportes](#9-privacidad-y-protección-de-datos-de-los-reportes)
10. [Principio de Divulgación Responsable (Responsible Disclosure)](#10-principio-de-divulgación-responsable-responsible-disclosure)
11. [Alineación con Estándares Internacionales de Ética en Seguridad](#11-alineación-con-estándares-internacionales-de-ética-en-seguridad)
12. [Preguntas Frecuentes sobre Ética y Legalidad](#12-preguntas-frecuentes-sobre-ética-y-legalidad)
13. [Declaración de Uso Educativo](#13-declaración-de-uso-educativo)

---

## 1. DECLARACIÓN DE PRINCIPIOS ÉTICOS

SecureScan Pro fue diseñado desde su concepción con la ética como **principio de diseño**, no como complemento tardío. Esto significa que las salvaguardas éticas y legales no son una sección del manual: están codificadas directamente en el sistema y no pueden desactivarse sin modificar el código fuente.

### 1.1 Principios rectores del proyecto

**Principio 1 — Autorización previa:** El análisis de seguridad sobre cualquier sistema sin autorización expresa y por escrito del propietario es ilegal e inmoral, independientemente de la intención del analista.

**Principio 2 — Proporcionalidad:** Las técnicas de análisis deben ser proporcionales al objetivo de la evaluación. SecureScan Pro usa técnicas de verificación, no de destrucción.

**Principio 3 — Mínimo privilegio:** El sistema opera con los permisos mínimos necesarios para cumplir su función. Los containers corren como usuarios no-root. Metasploit solo ejecuta módulos auxiliares.

**Principio 4 — Confinamiento:** Los laboratorios vulnerables están aislados en una red Docker cerrada. No tienen salida a Internet. No pueden ser alcanzados desde redes externas.

**Principio 5 — Trazabilidad:** Todas las peticiones a la API quedan registradas en los logs de Flask/Gunicorn. Los resultados de cada escaneo incluyen timestamps exactos. La trazabilidad permite auditar quién hizo qué y cuándo.

**Principio 6 — Divulgación responsable:** Si durante el uso del sistema en entornos propios se descubren vulnerabilidades, estas deben ser reportadas al propietario del sistema afectado antes de cualquier divulgación pública, siguiendo el proceso de Responsible Disclosure.

**Principio 7 — Propósito educativo:** Este sistema fue creado con el único propósito de aprender y enseñar ciberseguridad defensiva. Su finalidad es que los analistas comprendan cómo piensan los atacantes para poder construir mejores defensas.

---

## 2. MARCO LEGAL EN COLOMBIA

### 2.1 Ley 1273 de 2009 — Delitos Informáticos

La **Ley 1273 de 2009** ("Por medio de la cual se modifica el Código Penal, se crea un nuevo bien jurídico tutelado — denominado 'de la protección de la información y de los datos'") es la norma central que regula los delitos informáticos en Colombia.

**Artículos relevantes:**

| Artículo | Tipificación | Pena |
|---|---|---|
| **Art. 269A** | Acceso abusivo a un sistema informático (acceder sin autorización o permaneciendo contra la voluntad del titular) | 48 a 96 meses de prisión + multa |
| **Art. 269B** | Obstaculización ilegítima de sistema informático o red de telecomunicaciones | 48 a 96 meses + multa |
| **Art. 269C** | Interceptación de datos informáticos | 36 a 72 meses de prisión |
| **Art. 269D** | Daño informático (destruir, dañar, borrar, deteriorar, alterar o suprimir datos) | 48 a 96 meses + multa |
| **Art. 269E** | Uso de software malicioso (crear, adquirir, distribuir código malicioso) | 48 a 96 meses + multa |
| **Art. 269F** | Violación de datos personales | 48 a 96 meses + multa |
| **Art. 269G** | Suplantación de sitios web para capturar datos personales | 48 a 96 meses + multa |
| **Art. 269I** | Hurto por medios informáticos | 3 a 8 años + multa |

**Relación con SecureScan Pro:** El uso de SecureScan Pro sobre sistemas sin autorización podría constituir infracción del **Art. 269A** (acceso abusivo) y potencialmente del **Art. 269C** (interceptación de datos) y **Art. 269D** (si alguna herramienta causa daño involuntario). Por esta razón, el sistema implementa controles técnicos que hacen técnicamente difícil su uso fuera del laboratorio controlado.

**Excepción legal — Pruebas autorizadas:** El Art. 269A expresamente excluye de sanción el acceso a sistemas cuando existe **autorización expresa** del titular. Un contrato de pentesting o una carta de autorización por escrito es el documento legal que convierte una actividad potencialmente delictiva en un servicio legítimo.

### 2.2 Ley 1581 de 2012 — Protección de Datos Personales (Habeas Data)

La **Ley 1581 de 2012** regula el tratamiento de datos personales en Colombia. Es relevante para SecureScan Pro en dos dimensiones:

**Dimensión 1 — Datos encontrados durante el escaneo:** Un escaneo sobre un sistema real podría revelar datos personales de usuarios (nombres, correos, contraseñas en texto plano). Estos datos deben tratarse con confidencialidad estricta y no deben ser divulgados, almacenados permanentemente ni compartidos sin consentimiento.

**Dimensión 2 — Datos del reporte:** Los reportes generados por SecureScan Pro pueden contener información sensible sobre la postura de seguridad de una organización. Su tratamiento y distribución deben ser acordados con el cliente antes del análisis.

**Control técnico implementado:** Los reportes se almacenan localmente en el volumen Docker `scan-reports` con un TTL de 24 horas en Redis para escaneos completados. No se envían a servidores externos.

### 2.3 Decreto 1078 de 2015 — MinTIC

El **Decreto 1078 de 2015** del Ministerio de Tecnologías de la Información y las Comunicaciones regula el sector TIC en Colombia. Establece el marco de política para la seguridad de la información en entidades públicas, incluyendo la obligatoriedad de análisis de vulnerabilidades periódicos. Herramientas como SecureScan Pro contribuyen a cumplir este mandato cuando se usan en entornos propios.

### 2.4 Ley 1266 de 2008 — Habeas Data Financiero

Complementa la Ley 1581. Relevante si durante un análisis de seguridad se accede a bases de datos que contengan información financiera de personas naturales.

---

## 3. MARCO LEGAL INTERNACIONAL DE REFERENCIA

### 3.1 Estados Unidos — Computer Fraud and Abuse Act (CFAA)

La **CFAA (18 U.S.C. § 1030)** es la ley federal de EE.UU. que penaliza el acceso no autorizado a sistemas informáticos. Es relevante para SecureScan Pro porque varias de las herramientas integradas (Metasploit, SQLMap, Nuclei) fueron desarrolladas principalmente por organizaciones estadounidenses, y su uso puede estar sujeto a esta normativa en contextos transnacionales.

La CFAA ha sido interpretada en algunas instancias de forma muy amplia, penalizando incluso el acceso a información "pública" cuando los términos de servicio del sitio lo prohíben (caso United States vs. Nosal).

### 3.2 Unión Europea — Directiva 2013/40/UE y NIS2

La **Directiva 2013/40/UE** sobre ataques contra sistemas de información establece estándares mínimos de penalización armonizados en la UE para delitos informáticos similares a los de la Ley 1273 colombiana. La **Directiva NIS2 (2022/2555)** complementa esto con obligaciones de seguridad para operadores de servicios esenciales.

### 3.3 Convenio de Budapest sobre Ciberdelincuencia

El **Convenio de Budapest** (Council of Europe Treaty Series No. 185, 2001) es el primer tratado internacional sobre crímenes cometidos a través de Internet y sistemas informáticos. Colombia no es parte signataria, pero el convenio es la referencia internacional de facto para la tipificación de delitos informáticos, y la Ley 1273 de 2009 fue influenciada por él.

---

## 4. CONTROLES TÉCNICOS DE SEGURIDAD ÉTICA IMPLEMENTADOS EN EL CÓDIGO

Esta es la sección más importante del documento para SecureScan Pro: los controles éticos no son solo una política, están escritos en el código fuente y pueden verificarse directamente.

### 4.1 Validación multi-nivel de targets (`server/app.py`)

El sistema implementa cinco capas de validación antes de aceptar cualquier target:

**Capa 1 — Caracteres inválidos:**
```python
if any(c in target for c in ['@', ' ', '\\', '\n', '\r']):
    return False, "Target contains invalid characters"
```

**Capa 2 — Patrones de IPs privadas y loopback (10 patrones):**
```python
FORBIDDEN_PATTERNS = [
    r'^localhost',           # localhost explícito
    r'^127\.',               # Loopback IPv4 (127.0.0.0/8)
    r'^0\.0\.0\.0',         # Dirección cero
    r'^169\.254\.',          # Link-local (APIPA)
    r'^10\.',                # Red privada clase A (10.0.0.0/8)
    r'^192\.168\.',          # Red privada clase C (192.168.0.0/16)
    r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',  # Red privada clase B (172.16-31.x)
    r'^::1',                 # Loopback IPv6
    r'^fc00:',               # Unique local IPv6 (fc00::/7)
    r'^fe80:',               # Link-local IPv6 (fe80::/10)
]
```

**Capa 3 — Allowlist de targets del laboratorio:**
```python
ALLOWED_LAB_TARGETS = [
    t.strip() for t in os.environ.get(
        'ALLOWED_LAB_TARGETS',
        'juice-shop:3000,dvwa:80,webgoat:8080'
    ).split(',')
]
# Los hostnames de los labs siempre pasan — están en la allowlist
if any(
    hostname == allowed or hostname.startswith(allowed.split(':')[0])
    for allowed in ALLOWED_LAB_TARGETS
):
    return True, "Lab target allowed"
```

**Capa 4 — Modo restrictivo (opcional):**
```python
RESTRICT_TO_LAB = os.environ.get(
    'RESTRICT_TO_LAB_TARGETS', 'false'
).lower() == 'true'

if RESTRICT_TO_LAB:
    return False, (
        "Solo se permiten targets de laboratorio en modo restringido. "
        f"Targets permitidos: {', '.join(ALLOWED_LAB_TARGETS)}"
    )
```

Cuando `RESTRICT_TO_LAB_TARGETS=true` en `.env`, la API rechaza con `403 Forbidden` **cualquier** target que no sea exactamente uno de los tres labs, sin excepciones.

**Capa 5 — Validación de alcanzabilidad (configurable por petición):**
```python
def _validate_target_reachability(target: str, cfg: dict) -> tuple:
    # Verifica que el hostname resuelva en DNS
    if cfg.get('check_dns', True):
        socket.getaddrinfo(hostname, None)
    # Verifica que el puerto esté abierto (TCP connect)
    if cfg.get('check_reachability', True):
        with socket.create_connection((hostname, port), timeout=timeout):
            pass
```

**Capa 6 — Validación de UUID v4 para scan IDs:**
```python
def validate_scan_id(scan_id: str) -> bool:
    try:
        uuid_module.UUID(scan_id, version=4)
        return True
    except (ValueError, AttributeError):
        return False
```

Todo `scan_id` recibido en cualquier endpoint es validado como UUID v4 antes de cualquier operación. Esto previene inyección de caracteres en las claves de Redis.

### 4.2 Autenticación por token API (`server/app.py`)

```python
API_TOKEN = os.environ.get('API_TOKEN', '')
if not API_TOKEN:
    logger.warning(
        "API_TOKEN no configurado — todos los endpoints son accesibles "
        "sin autenticación. Configura API_TOKEN en .env para entornos expuestos."
    )

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
                return jsonify({'error': 'Unauthorized — invalid or missing API token'}), 401
        return f(*args, **kwargs)
    return decorated
```

Cuando `API_TOKEN` está configurado, **todos** los endpoints sensibles requieren el header `X-API-Token: <token>`. Los intentos de acceso no autorizados quedan registrados en los logs con la dirección IP del solicitante.

### 4.3 Rate limiting (`server/app.py`)

```python
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri=redis_url,
    default_limits=["500 per day", "100 per hour"]
)

@app.route('/api/scan', methods=['POST'])
@require_token
@limiter.limit("20 per hour")
def start_scan():
    ...
```

El endpoint más sensible (`POST /api/scan`) está limitado a **20 peticiones por hora por IP**. Esto previene el uso automatizado masivo del sistema para atacar múltiples objetivos sin detección.

### 4.4 Circuit Breaker (`server/app.py`)

```python
def _cb_is_open(target: str, cfg: dict) -> bool:
    threshold = cfg.get('failure_threshold', 3)  # 3 fallos consecutivos
    recovery  = cfg.get('recovery_timeout', 60)  # 60 segundos de bloqueo
    ...

def _cb_record_failure(target: str) -> None:
    # Incrementa el contador de fallos y abre el circuito
    state['failures'] = state.get('failures', 0) + 1
    state['opened_at'] = time.time()
    logger.warning(
        "Circuit breaker: %d fallos para %s",
        state['failures'], target[:80]
    )
```

El Circuit Breaker previene que el sistema genere una ráfaga de peticiones contra un objetivo que está fallando. Esto protege tanto al objetivo como al operador, evitando comportamientos que podrían interpretarse como un ataque DoS inadvertido.

### 4.5 Aislamiento de red Docker (`docker-compose.yml`)

```yaml
networks:
  securescan-net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16   # Servicios de infraestructura
  lab-net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.21.0.0/16   # Laboratorios vulnerables AISLADOS
```

Los laboratorios (DVWA, Juice Shop, WebGoat) están **exclusivamente** en `lab-net`. No tienen acceso a `securescan-net` ni a Internet. Un atacante que comprometa uno de los labs no puede pivotar hacia la infraestructura principal ni hacia la red del host.

### 4.6 Usuarios no-root en los containers

```dockerfile
# server/Dockerfile
RUN groupadd -r scanner && useradd -r -g scanner -d /home/scanner -m -s /bin/bash scanner
# ...
USER scanner   ← El proceso Flask/Gunicorn corre como "scanner", no como root
```

```dockerfile
# Dockerfile.frontend
RUN addgroup --system --gid 1001 nodejs
RUN adduser  --system --uid 1001 nextjs
USER nextjs   ← Next.js corre como "nextjs", no como root
```

Si un atacante explotara una vulnerabilidad en la API o el frontend, el proceso comprometido tendría permisos de usuario no-privilegiado (`scanner` o `nextjs`), limitando significativamente el daño potencial.

### 4.7 Seguridad del container API

```yaml
# docker-compose.yml
cap_add:
  - NET_RAW    # Solo para nmap — raw socket access
  - NET_ADMIN  # Solo para nmap — network administration
security_opt:
  - no-new-privileges:true  # El proceso no puede escalar privilegios
```

La directiva `no-new-privileges:true` impide que cualquier proceso dentro del container pueda ganar nuevos privilegios mediante setuid, setgid o capabilities de archivo.

### 4.8 Redis y SQLMap API — Binding solo a localhost

```yaml
# docker-compose.yml
redis:
  ports:
    - "127.0.0.1:6379:6379"   # Solo accesible desde localhost

sqlmapapi:
  ports:
    - "127.0.0.1:8775:8775"   # Solo accesible desde localhost
```

Redis y la SQLMap API **no** están expuestos en `0.0.0.0` (todas las interfaces). Solo pueden ser alcanzados desde el host local (`127.0.0.1`), no desde otras máquinas en la misma red local.

### 4.9 Metasploit — Solo módulos auxiliares

```python
# server/modules/metasploit.py
_BASE_WEB: List[Tuple] = [
    ("auxiliary/scanner/http/http_version",  {"THREADS": 5}, "info",   30),
    ("auxiliary/scanner/http/options",       {"THREADS": 5}, "medium", 30),
    ("auxiliary/scanner/http/dir_listing",   {"THREADS": 5}, "medium", 45),
    ("auxiliary/scanner/http/robots_txt",    {},              "info",   30),
]
```

Todos los módulos Metasploit usados por SecureScan Pro son **auxiliares de escaneo** (`auxiliary/scanner/`), nunca módulos de explotación activa (`exploits/`) ni payloads (`payload/`). Esta distinción técnica es fundamental: los módulos auxiliares *verifican* si una vulnerabilidad existe; los módulos de explotación la *explotan* para obtener acceso. SecureScan Pro solo hace lo primero.

### 4.10 Sanitización XSS en reportes (`server/utils/reporter.py`)

```python
def sanitize_html(text: Any) -> str:
    """Sanitize text for HTML output to prevent XSS"""
    if text is None:
        return ''
    text = str(text)
    return html.escape(text, quote=True)
```

Todo contenido de los hallazgos de seguridad (nombres de vulnerabilidades, payloads, URLs, evidencias) se sanitiza con `html.escape(text, quote=True)` antes de ser insertado en el reporte HTML. Esto previene que un payload XSS encontrado durante el escaneo se ejecute al abrir el reporte en el navegador.

### 4.11 Headers de seguridad en el frontend (`next.config.mjs`)

```javascript
headers: [
  { key: 'X-Content-Type-Options',   value: 'nosniff' },
  { key: 'X-Frame-Options',          value: 'DENY' },
  { key: 'X-XSS-Protection',         value: '1; mode=block' },
  { key: 'Referrer-Policy',          value: 'strict-origin-when-cross-origin' },
  { key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=(), interest-cohort=()' },
  { key: 'Content-Security-Policy',
    value: "default-src 'self'; frame-ancestors 'none'; base-uri 'self'; ..." }
]
```

El frontend implementa **Content Security Policy (CSP) completo**, elimina el header `X-Powered-By` (`poweredByHeader: false`) y aplica seis cabeceras de seguridad en todas las respuestas HTTP. `frame-ancestors 'none'` previene que la aplicación sea embebida en iframes (protección contra clickjacking).

### 4.12 Validación de SECRET_KEY en producción (`server/app.py`)

```python
_secret_key = os.environ.get('SECRET_KEY', '')
if not _secret_key or 'CAMBIA' in _secret_key or 'change' in _secret_key.lower():
    if os.environ.get('FLASK_ENV') != 'development':
        raise RuntimeError(
            "SECRET_KEY debe ser una clave segura en producción."
        )
    logger.warning("Usando SECRET_KEY de desarrollo — NO usar en producción.")
```

El sistema se **niega a arrancar** en modo producción si `SECRET_KEY` contiene las cadenas de ejemplo. Esto previene despliegues accidentales con claves predecibles que podrían comprometer las sesiones de Flask.

---

## 5. USO AUTORIZADO Y USO NO AUTORIZADO

### 5.1 Usos AUTORIZADOS y LEGALES de SecureScan Pro

| Escenario | Autorización requerida | Descripción |
|---|---|---|
| Laboratorio SENA con los 3 labs incluidos | ✅ Ninguna adicional — los labs son para eso | DVWA, Juice Shop y WebGoat son aplicaciones diseñadas para ser atacadas |
| Sistema propio del operador (VPS, servidor personal) | ✅ Propia (el operador ES el propietario) | El operador tiene autorización implícita sobre sus propios sistemas |
| Sistema del empleador en contexto laboral | ✅ Autorización escrita del empleador | Bug bounty corporativo, evaluación de seguridad interna |
| Sistema de un cliente de consultoría | ✅ Contrato de pentesting firmado | Evaluación de seguridad profesional para terceros |
| CTF (Capture The Flag) | ✅ Las reglas del CTF constituyen la autorización | Competencias de hacking ético |
| Entorno de laboratorio propio (VMs locales) | ✅ Propia (el operador controla el entorno) | Lab personal de práctica |

### 5.2 Usos NO AUTORIZADOS e ILEGALES

| Escenario | Por qué es ilegal | Norma aplicable |
|---|---|---|
| Escanear un sitio web de una empresa sin permiso | Acceso no autorizado aunque el sitio sea "público" | Art. 269A Ley 1273/2009, CFAA |
| Escanear la red del vecino o de la empresa vecina | Acceso abusivo a sistema de terceros | Art. 269A Ley 1273/2009 |
| Usar el sistema para realizar ataques DoS | Obstaculización ilegítima de sistema | Art. 269B Ley 1273/2009 |
| Extraer datos de usuarios de un sistema escaneado | Violación de datos personales | Art. 269F Ley 1273/2009, Ley 1581/2012 |
| Escanear infraestructura gubernamental sin permiso | Agravante por objetivo crítico — penas mayores | Art. 269A + agravantes Ley 1273/2009 |
| Modificar el código para eludir los controles de targets | Conversión del sistema en herramienta de ataque | Art. 269E (uso de software malicioso) |
| Compartir el sistema con terceros para ataques | Coautoría o complicidad en delito informático | Arts. 269A, 269E Ley 1273/2009 |

### 5.3 ¿Qué pasa si el sitio web dice "hackéame" o tiene un bug bounty?

Algunos sitios web tienen programas de **bug bounty** (recompensa por vulnerabilidades) como HackerOne o Bugcrowd. En ese caso:

- El alcance (scope) del programa define exactamente qué sistemas pueden ser probados.
- Las técnicas permitidas están especificadas en las reglas del programa.
- Usar herramientas automatizadas como SecureScan Pro puede estar prohibido en algunos programas (revisar siempre las reglas).
- Si el programa lo permite, SecureScan Pro puede ser una herramienta válida para el reconocimiento inicial.

**Regla general:** Leer siempre las reglas del programa de bug bounty antes de iniciar cualquier análisis y ceñirse estrictamente a ellas.

---

## 6. LOS TRES LABORATORIOS — POR QUÉ SON LEGALES Y SEGUROS

### 6.1 OWASP Juice Shop

**Licencia:** MIT License  
**Propósito declarado por sus autores:** *"OWASP Juice Shop is probably the most modern and sophisticated insecure web application! It can be used in security trainings, awareness demos, CTFs and as a guinea pig for security tools!"*  
**Repositorio oficial:** https://github.com/juice-shop/juice-shop  
**Mantenido por:** Bjoern Kimminich y OWASP Foundation

Juice Shop es explícitamente diseñada para ser atacada. Su código fuente contiene las vulnerabilidades de forma intencional y documentada. No hay ningún usuario real, ningún dato personal real, ningún sistema de producción involucrado.

### 6.2 DVWA (Damn Vulnerable Web Application)

**Licencia:** GNU General Public License v3.0  
**Propósito declarado:** *"Damn Vulnerable Web Application (DVWA) is a PHP/MySQL web application that is damn vulnerable. Its main goal is to be an aid for security professionals to test their skills and tools in a legal environment, help web developers better understand the processes of securing web applications."*  
**Repositorio oficial:** https://github.com/digininja/DVWA  
**Mantenido por:** Robin Wood (digininja) y la comunidad

DVWA fue creada específicamente para entrenamiento legal. Su documentación incluye advertencias sobre **no desplegarla en servidores accesibles desde Internet** sin controles adicionales, ya que la aplicación en sí es una puerta de entrada. En SecureScan Pro, DVWA está en la red Docker aislada `lab-net`, cumpliendo esta recomendación.

### 6.3 WebGoat

**Licencia:** Apache License 2.0  
**Propósito declarado:** *"WebGoat is a deliberately insecure web application maintained by OWASP designed to teach web application security lessons."*  
**Repositorio oficial:** https://github.com/WebGoat/WebGoat  
**Mantenido por:** OWASP Foundation

WebGoat es la plataforma educativa más antigua de OWASP, con más de 20 años de uso en formación en seguridad. Incluye lecciones interactivas donde el aprendiz explota vulnerabilidades y luego aprende cómo remediarlas.

### 6.4 Configuración de aislamiento en SecureScan Pro

Los tres laboratorios están configurados con las siguientes medidas de aislamiento:

```yaml
# docker-compose.yml — configuración de los labs
juice-shop:
  networks:
    - lab-net      # Solo en lab-net, NO en securescan-net, NO en Internet

dvwa:
  networks:
    - lab-net      # Ídem

webgoat:
  networks:
    - lab-net      # Ídem
```

Ningún laboratorio tiene acceso a Internet. Ningún laboratorio puede comunicarse con `securescan-net` (donde está Redis, la API y el frontend). Están completamente confinados dentro de la red `172.21.0.0/16`.

---

## 7. METASPLOIT EN MODO AUXILIAR — DISTINCIÓN TÉCNICA Y ÉTICA

### 7.1 La distinción entre verificar y explotar

Metasploit Framework tiene tres tipos principales de módulos:

| Tipo | Prefijo | Acción | Uso en SecureScan Pro |
|---|---|---|---|
| **Auxiliares** | `auxiliary/` | Escaneo, enumeración, *verificación* de si una vulnerabilidad existe | ✅ **Sí — son los únicos usados** |
| **Exploits** | `exploits/` | *Explotar* activamente la vulnerabilidad para ganar acceso | ❌ Nunca usados |
| **Post-explotación** | `post/` | Actividades después de comprometer un sistema (persistencia, pivoting) | ❌ Nunca usados |
| **Payloads** | `payload/` | Código malicioso ejecutado en el sistema comprometido | ❌ Nunca usados |

### 7.2 Módulos auxiliares usados en SecureScan Pro

```python
# server/modules/metasploit.py — _BASE_WEB
_BASE_WEB = [
    # Enumeración de información HTTP — NO modifica nada en el objetivo
    ("auxiliary/scanner/http/http_version",  {"THREADS": 5}, "info",   30),
    ("auxiliary/scanner/http/options",       {"THREADS": 5}, "medium", 30),
    ("auxiliary/scanner/http/dir_listing",   {"THREADS": 5}, "medium", 45),
    ("auxiliary/scanner/http/robots_txt",    {},              "info",   30),
]

# Módulos auxiliares adicionales por tecnología (todos son /auxiliary/scanner/)
# Apache Tomcat:
("auxiliary/scanner/http/tomcat_mgr_login", ...)   # Verifica si el login por defecto funciona
("auxiliary/scanner/http/tomcat_enum",       ...)   # Enumera aplicaciones desplegadas

# PHP:
("auxiliary/scanner/http/php_cgi_arg_injection", ...)   # Verifica si el bug PHP-CGI existe
("auxiliary/scanner/http/phpinfo",               ...)   # Verifica si phpinfo() está expuesto
```

Ninguno de estos módulos *compromete* el sistema. Verifican si una condición de vulnerabilidad existe y reportan el resultado, exactamente como lo haría nmap con sus scripts NSE.

### 7.3 Modo simulación automático

Si `msfrpcd` no está disponible o falla la conexión RPC, el módulo activa automáticamente el modo simulación:

```python
# server/modules/metasploit.py
try:
    from pymetasploit3.msfrpc import MsfRpcClient
    _MSF_AVAILABLE = True
except ImportError:
    _MSF_AVAILABLE = False

def scan(self, target, ...):
    if not _MSF_AVAILABLE:
        return self._simulate_scan(target, ...)
```

Los resultados simulados incluyen `"simulated": True` para que el dashboard los distinga claramente de resultados reales.

---

## 8. RESPONSABILIDADES DEL OPERADOR

### 8.1 Antes de cualquier escaneo

El operador de SecureScan Pro tiene la responsabilidad de:

1. **Verificar que tiene autorización:** Propietario del sistema, contrato firmado, o uso dentro del laboratorio incluido.
2. **Revisar el alcance:** Si hay una autorización externa, verificar exactamente qué sistemas y técnicas están permitidos.
3. **Configurar el modo restrictivo si corresponde:** Si el sistema va a ser usado por múltiples personas, activar `RESTRICT_TO_LAB_TARGETS=true` en `.env`.
4. **Verificar el estado de los labs:** Asegurarse de que los targets del escaneo son los laboratorios incluidos, no sistemas de terceros.

### 8.2 Durante el escaneo

5. **No interrumpir escaneos activos sobre sistemas productivos:** Un escaneo interrumpido a mitad puede dejar el sistema objetivo en estado inconsistente.
6. **Monitorear el consumo de recursos:** ZAP con escaneo activo puede generar carga significativa sobre el objetivo. En sistemas productivos, coordinar con el equipo de operaciones.
7. **No compartir las credenciales de la API:** Si `API_TOKEN` está configurado, es un secreto operacional que no debe exponerse.

### 8.3 Después del escaneo

8. **Tratar el reporte con confidencialidad:** El reporte contiene información sensible sobre debilidades del sistema. Solo debe ser accesible a las personas autorizadas.
9. **Reportar los hallazgos al propietario:** Si el escaneo es sobre un sistema de un cliente, los hallazgos deben ser comunicados formalmente y dentro del plazo acordado.
10. **Eliminar los datos del escaneo cuando ya no sean necesarios:** Los datos en Redis tienen TTL de 24h para escaneos completados. Los reportes en disco deben eliminarse cuando ya no sean necesarios.
11. **No divulgar vulnerabilidades sin autorización:** Publicar vulnerabilidades encontradas en sistemas de terceros sin su consentimiento es un delito en Colombia (Art. 269F y potencialmente 269G).

### 8.4 Responsabilidad sobre el uso del sistema por terceros

Si el operador comparte el acceso al sistema con otras personas (compañeros, estudiantes, clientes), asume la responsabilidad de:

- Instruirles sobre el marco legal y ético.
- Asegurarse de que solo escaneen targets autorizados.
- Configurar `API_TOKEN` para controlar quién puede iniciar escaneos.
- Mantener los logs para auditoría.

---

## 9. PRIVACIDAD Y PROTECCIÓN DE DATOS DE LOS REPORTES

### 9.1 Qué datos almacena el sistema

| Dato | Dónde se almacena | TTL | Quién puede accederlo |
|---|---|---|---|
| Estado del escaneo (pasos, progreso) | Redis / memoria | 3600s (running), 86400s (completed) | API con token |
| Resultados del escaneo (vulnerabilidades, tecnologías, etc.) | Redis / memoria | 86400s (24h) | API con token |
| Reportes generados (HTML, PDF, JSON, CSV) | Volumen Docker `scan-reports` | Sin TTL automático — eliminación manual | Acceso al container |
| Logs de Flask/Gunicorn | stdout del container | Hasta reinicio del container | Acceso al host |

### 9.2 Datos que NO se almacenan

- Credenciales de los usuarios de los sistemas escaneados (Patator solo reporta que encontró una credencial válida, no la almacena en texto plano en Redis).
- Datos personales extraídos de las bases de datos durante SQLi.
- Capturas de tráfico de red.
- Cookies de sesión de los usuarios reales de los sistemas escaneados.

> **Nota:** La cookie de sesión usada por el auto-login de SecureScan Pro es la de la cuenta de prueba del laboratorio (ej: `admin@juice-sh.op`), no de usuarios reales.

### 9.3 Eliminación segura de reportes

```bash
# Eliminar todos los reportes del volumen Docker
docker compose exec api find /app/reports -name "report-*.html" \
                                          -name "report-*.pdf" \
                                          -name "report-*.json" \
                                          -name "report-*.csv" \
                                          -delete

# Eliminar todos los escaneos de Redis
docker compose exec redis \
  redis-cli -a "${REDIS_PASSWORD}" FLUSHDB
```

### 9.4 Clasificación de confidencialidad recomendada para reportes

| Tipo de entorno escaneado | Clasificación recomendada |
|---|---|
| Laboratorio SENA (DVWA, Juice Shop, WebGoat) | Sin clasificación especial (datos sintéticos) |
| Sistema propio de práctica | USO INTERNO |
| Sistema de cliente en contexto profesional | CONFIDENCIAL |
| Sistema de infraestructura crítica | SECRETO — distribución restringida |

---

## 10. PRINCIPIO DE DIVULGACIÓN RESPONSABLE (RESPONSIBLE DISCLOSURE)

### 10.1 ¿Qué es Responsible Disclosure?

La **divulgación responsable** (también llamada **coordinated vulnerability disclosure**) es el proceso por el cual un investigador de seguridad que encuentra una vulnerabilidad en un sistema que no es suyo:

1. Notifica primero al propietario del sistema afectado con todos los detalles técnicos.
2. Le da un tiempo razonable para corregir la vulnerabilidad (generalmente 90 días, siguiendo el estándar de Google Project Zero).
3. Solo después de que la vulnerabilidad fue corregida (o pasó el plazo), la divulga públicamente.

### 10.2 Por qué importa en el contexto de SecureScan Pro

Si un aprendiz usa SecureScan Pro en un sistema con autorización (ej: un bug bounty, un sistema de su empleador) y descubre vulnerabilidades reales, debe seguir el proceso de Responsible Disclosure:

**Paso 1 — Documentar:** Guardar el reporte generado por SecureScan Pro con todos los hallazgos, incluyendo URLs, payloads y evidencias.

**Paso 2 — Contactar al propietario:** Enviar el reporte al equipo de seguridad del propietario (generalmente security@empresa.com o a través de la plataforma de bug bounty si existe).

**Paso 3 — Dar tiempo para corregir:** Acordar un plazo razonable. La industria estándar es 90 días.

**Paso 4 — No explotar:** Nunca usar las vulnerabilidades encontradas para beneficio propio ni para causar daño, incluso si la empresa no responde.

**Paso 5 — Divulgación coordinada:** Si el plazo vence sin respuesta o sin corrección, notificar que se procederá a publicar y darle un plazo adicional (generalmente 7-14 días).

### 10.3 Organizaciones de referencia en Responsible Disclosure

| Organización | Recurso |
|---|---|
| CERT/CC (Carnegie Mellon) | https://www.kb.cert.org/vuls/report/ |
| Google Project Zero | https://googleprojectzero.blogspot.com/p/vulnerability-disclosure-faq.html |
| CISA (EE.UU.) | https://www.cisa.gov/coordinated-vulnerability-disclosure-process |
| OWASP | https://owasp.org/www-community/vulnerabilities/ |
| HackerOne | https://hackerone.com/disclosure-guidelines |
| Bugcrowd | https://www.bugcrowd.com/resources/levelup/responsible-disclosure/ |

---

## 11. ALINEACIÓN CON ESTÁNDARES INTERNACIONALES DE ÉTICA EN SEGURIDAD

### 11.1 Código de Ética de EC-Council (CEH)

El **EC-Council** es la organización que certifica al Certified Ethical Hacker (CEH). Su código de ética establece que los profesionales certificados deben:

- Mantener la privacidad y confidencialidad de la información.
- No acceder a sistemas sin autorización explícita.
- No usar sus habilidades para dañar a terceros.
- Reportar vulnerabilidades a los propietarios.

SecureScan Pro está alineado con estos principios: los controles de target, el modo auxiliar de Metasploit y el proceso de Responsible Disclosure son implementaciones directas de estos compromisos éticos.

### 11.2 Código de Ética de (ISC)² — CISSP

El **International Information System Security Certification Consortium** establece en su código de ética cuatro cánones:

1. Proteger la sociedad, el bien común, la confianza y la infraestructura necesaria.
2. Actuar de forma honorable, honesta, justa, responsable y legal.
3. Proveer servicio diligente y competente a los empleadores.
4. Hacer avanzar y proteger la profesión.

El propósito educativo de SecureScan Pro —enseñar ciberseguridad defensiva usando herramientas reales en un entorno controlado— contribuye directamente al Canon 1 (proteger la infraestructura mediante la formación de defensores competentes) y al Canon 4 (hacer avanzar la profesión).

### 11.3 OWASP Code of Ethics

OWASP en su Code of Ethics para desarrolladores de herramientas de seguridad establece que estas deben:

- Ser diseñadas para uso defensivo y educativo.
- Incluir documentación clara sobre uso legal y ético.
- No facilitar ataques contra sistemas sin autorización.

SecureScan Pro cumple los tres puntos: diseño orientado a laboratorio educativo, este documento como evidencia de documentación ética, y los controles técnicos de `FORBIDDEN_PATTERNS` y `RESTRICT_TO_LAB_TARGETS` como implementación técnica del tercer punto.

### 11.4 PTES — Penetration Testing Execution Standard

El **PTES** establece como fase 0 (pre-engagement) la obtención de **autorización formal por escrito** antes de iniciar cualquier actividad de pentesting. SecureScan Pro refleja esto en su diseño: el auto-login implementado solo funciona sobre los labs incluidos, que son la "autorización implícita" del entorno educativo.

---

## 12. PREGUNTAS FRECUENTES SOBRE ÉTICA Y LEGALIDAD

### P1: ¿Puedo usar SecureScan Pro para analizar el sitio web de mi universidad?

**Respuesta:** No, a menos que tengas autorización expresa y por escrito del área de tecnología de tu universidad. El hecho de ser estudiante de la institución no te da autorización para escanear sus sistemas. Solicita permiso formalmente antes de hacerlo.

### P2: ¿Está bien escanear un sitio web que no tiene login ni datos personales?

**Respuesta:** No. La ausencia de datos personales o de autenticación no hace legal el acceso no autorizado. La Ley 1273 de 2009 Art. 269A penaliza el acceso a cualquier sistema informático sin autorización, independientemente de su contenido.

### P3: ¿Puedo usar SecureScan Pro en el trabajo para analizar los sistemas de mi empleador?

**Respuesta:** Depende. Si tu rol laboral incluye responsabilidades de seguridad y tienes autorización (explícita o implícita por tu cargo) para realizar pruebas de seguridad, sí. Si no estás seguro, pide autorización por escrito a tu empleador antes de proceder.

### P4: ¿El hecho de que SecureScan Pro tenga controles que impiden escanear IPs privadas me protege legalmente?

**Respuesta:** Los controles técnicos son una medida de seguridad y una evidencia de buena fe en el diseño del sistema. Sin embargo, no constituyen una exención legal automática. Si alguien modifica el código para eludir esos controles y usa el sistema de forma ilegal, asume plena responsabilidad penal.

### P5: ¿Qué pasa si durante un escaneo autorizado encuentro vulnerabilidades críticas?

**Respuesta:** Docúmenlas con el reporte de SecureScan Pro, notifica inmediatamente al propietario del sistema con todos los detalles técnicos, y no compartas esa información con terceros hasta que la vulnerabilidad sea corregida (proceso de Responsible Disclosure).

### P6: ¿Puedo compartir SecureScan Pro con mis compañeros del SENA?

**Respuesta:** Sí, el código es de código abierto para uso educativo. Asegúrate de que quienes reciban el sistema también comprendan el marco ético y legal de su uso. Comparte también este documento junto con el sistema.

### P7: ¿Puedo usar SecureScan Pro en una Hackathon o CTF?

**Respuesta:** Sí, siempre que las reglas de la competencia lo permitan. Las reglas del CTF o Hackathon constituyen la autorización. Lee las reglas antes de usar herramientas automatizadas, ya que algunas competencias las prohíben expresamente.

### P8: ¿Es legal tener Metasploit instalado en mi computadora?

**Respuesta:** En Colombia, la mera posesión de herramientas de seguridad (incluyendo Metasploit) no es ilegal. Lo que es ilegal es su uso para acceder a sistemas sin autorización (Art. 269A y 269E Ley 1273). Metasploit es usado legítimamente por miles de profesionales de seguridad en todo el mundo.

---

## 13. DECLARACIÓN DE USO EDUCATIVO

### 13.1 Declaración formal

**Yo, el aprendiz Marlon, declaro que:**

El proyecto **SecureScan Pro v3.0** fue desarrollado con el propósito exclusivo de aprender, practicar y demostrar competencias en seguridad de aplicaciones web en el marco del programa **Técnico en Seguridad de Aplicaciones Web del SENA**.

Todos los análisis de seguridad realizados durante el desarrollo y las pruebas del sistema se efectuaron sobre los laboratorios vulnerables incluidos (DVWA, OWASP Juice Shop y WebGoat), que son aplicaciones de código abierto diseñadas específicamente para ese propósito, sin intervenir en ningún sistema real de terceros sin autorización.

El sistema implementa controles técnicos que dificultan activamente su uso no autorizado, incluyendo la validación de targets, el aislamiento de red Docker, el modo restrictivo de laboratorio y la limitación de Metasploit a módulos auxiliares de verificación.

### 13.2 Compromiso de uso responsable

Al usar SecureScan Pro, el operador acepta implícitamente:

1. **Solo** escanear sistemas sobre los cuales tenga autorización expresa o implícita como propietario.
2. **Tratar** todos los resultados obtenidos con confidencialidad apropiada al contexto.
3. **No modificar** los controles de seguridad éticos del sistema para eludir las restricciones de targets.
4. **Reportar** cualquier vulnerabilidad real descubierta siguiendo el proceso de Responsible Disclosure.
5. **Asumir** plena responsabilidad legal y ética por cualquier uso del sistema fuera del laboratorio educativo incluido.

### 13.3 Licencia de uso educativo

SecureScan Pro es un proyecto de código abierto de carácter educativo, desarrollado en el marco del programa formativo del SENA. Su código puede ser estudiado, modificado y utilizado para fines educativos, siempre que se respete el presente marco ético y legal.

**Las herramientas integradas tienen sus propias licencias:**

| Herramienta | Licencia |
|---|---|
| Nmap | Nmap Public Source License (NPSL) |
| OWASP ZAP | Apache License 2.0 |
| SQLMap | GNU General Public License v2.0 |
| Nuclei | MIT License |
| Gobuster | Apache License 2.0 |
| ffuf | MIT License |
| Metasploit Framework | BSD 3-Clause "New" License |
| Searchsploit / ExploitDB | GNU General Public License v2.0 |
| Patator | GNU General Public License v2.0 |
| DVWA | GNU General Public License v3.0 |
| OWASP Juice Shop | MIT License |
| WebGoat | Apache License 2.0 |

---

## REFERENCIAS LEGALES Y NORMATIVAS

### Legislación colombiana

- Congreso de Colombia. (2009). *Ley 1273 de 2009 — Protección de la información y de los datos*. https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=34492
- Congreso de Colombia. (2008). *Ley 1266 de 2008 — Habeas Data Financiero*. https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=34488
- Congreso de Colombia. (2012). *Ley 1581 de 2012 — Protección de Datos Personales*. https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981
- Presidencia de la República. (2015). *Decreto 1078 de 2015 — Decreto Único Reglamentario Sector TIC*. https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=72925

### Normativa internacional de referencia

- Council of Europe. (2001). *Convention on Cybercrime (Budapest Convention)*. https://www.coe.int/en/web/conventions/full-list/-/conventions/treaty/185
- European Parliament. (2013). *Directive 2013/40/EU on attacks against information systems*. https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32013L0040
- U.S. Department of Justice. (2020). *Computer Fraud and Abuse Act (18 U.S.C. § 1030)*. https://www.justice.gov/jm/jm-9-48000-computer-fraud

### Estándares y marcos éticos

- EC-Council. (2023). *CEH Code of Ethics*. https://www.eccouncil.org/code-of-ethics/
- (ISC)². (2023). *Code of Ethics*. https://www.isc2.org/Ethics
- OWASP Foundation. (2023). *OWASP Code of Ethics*. https://owasp.org/www-policy/legal/code-of-ethics
- PTES Technical Guidelines. (2012). *Penetration Testing Execution Standard*. http://www.pentest-standard.org/index.php/Pre-engagement
- NIST. (2022). *NIST SP 800-115: Technical Guide to Information Security Testing and Assessment*. https://csrc.nist.gov/publications/detail/sp/800-115/final

### Laboratorios vulnerables — Términos de uso

- OWASP Juice Shop. *Legal Notice*. https://github.com/juice-shop/juice-shop/blob/master/LICENSE
- DVWA. *Legal Disclaimer*. https://github.com/digininja/DVWA/blob/master/README.md#legal
- WebGoat. *Apache License 2.0*. https://github.com/WebGoat/WebGoat/blob/develop/LICENSE

### Responsible Disclosure

- Google Project Zero. (2023). *Vulnerability Disclosure Policy*. https://googleprojectzero.blogspot.com/p/vulnerability-disclosure-faq.html
- CISA. (2023). *Coordinated Vulnerability Disclosure Process*. https://www.cisa.gov/coordinated-vulnerability-disclosure-process
- ISO/IEC 29147:2018. *Information technology — Security techniques — Vulnerability disclosure*. https://www.iso.org/standard/72311.html

---

*Documento elaborado como parte del Proyecto de Grado — Técnico en Seguridad de Aplicaciones Web.*  
*SENA — Servicio Nacional de Aprendizaje — Colombia, 2026*  
*Los controles técnicos descritos en la Sección 4 pueden verificarse directamente en el código fuente:*  
*`server/app.py`, `server/modules/metasploit.py`, `server/utils/reporter.py`, `docker-compose.yml`, `next.config.mjs`*
