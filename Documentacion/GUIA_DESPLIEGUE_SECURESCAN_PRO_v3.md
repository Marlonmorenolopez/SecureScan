# GUÍA DE DESPLIEGUE COMPLETA
## SecureScan Pro v3.0 — Instalación, Configuración y Operación

**Autor:** Tecnico en Seguridad de Aplicaciones Web   
**Institución:** SENA — Servicio Nacional de Aprendizaje (Colombia)  
**Programa:** Técnico en Seguridad de Aplicaciones Web  
**Versión del sistema:** 3.0 (backend v5.0 / Dockerfile v3.1.3)  
**Fecha de actualización:** Junio 2026  
**Entorno de destino:** Kali Linux en VirtualBox / Ubuntu 24 LTS  

---

## TABLA DE CONTENIDOS

1. [Requisitos del Sistema](#1-requisitos-del-sistema)
2. [Prerequisitos de Software](#2-prerequisitos-de-software)
3. [Obtención del Código Fuente](#3-obtención-del-código-fuente)
4. [Configuración de Variables de Entorno (.env)](#4-configuración-de-variables-de-entorno-env)
5. [Despliegue Automático con start.sh (Método Recomendado)](#5-despliegue-automático-con-startsh-método-recomendado)
6. [Despliegue Manual Paso a Paso](#6-despliegue-manual-paso-a-paso)
7. [Verificación del Despliegue](#7-verificación-del-despliegue)
8. [Tiempos de Arranque por Servicio](#8-tiempos-de-arranque-por-servicio)
9. [Mapa de Puertos y URLs de Acceso](#9-mapa-de-puertos-y-urls-de-acceso)
10. [Credenciales del Laboratorio](#10-credenciales-del-laboratorio)
11. [Operación Diaria — Comandos Esenciales](#11-operación-diaria--comandos-esenciales)
12. [Gestión de Logs](#12-gestión-de-logs)
13. [Gestión de Volúmenes y Datos Persistentes](#13-gestión-de-volúmenes-y-datos-persistentes)
14. [Actualización del Sistema](#14-actualización-del-sistema)
15. [Desarrollo Local (sin Docker)](#15-desarrollo-local-sin-docker)
16. [Troubleshooting — Problemas Frecuentes y Soluciones](#16-troubleshooting--problemas-frecuentes-y-soluciones)
17. [Referencia Completa de Variables de Entorno](#17-referencia-completa-de-variables-de-entorno)
18. [Arquitectura de Redes Docker](#18-arquitectura-de-redes-docker)
19. [Consideraciones de Seguridad en el Despliegue](#19-consideraciones-de-seguridad-en-el-despliegue)

---

## 1. REQUISITOS DEL SISTEMA

### 1.1 Hardware mínimo recomendado

| Recurso | Mínimo | Recomendado |
|---|---|---|
| CPU | 4 núcleos | 6+ núcleos |
| RAM | 8 GB | 16 GB |
| Almacenamiento | 25 GB libres | 40 GB libres |
| Tipo de disco | HDD | SSD (mejora tiempos de build) |
| Arquitectura | x86_64 / amd64 | x86_64 / amd64 |

> **Nota sobre RAM:** OWASP ZAP requiere 3 GB de límite de memoria (configurado en el docker-compose.yml). Metasploit Framework requiere aproximadamente 1.5 GB adicionales. Con todos los servicios corriendo simultáneamente, el uso total de RAM puede llegar a 10-12 GB en escaneos activos.

> **Nota sobre almacenamiento:** Las imágenes Docker construidas ocupan aproximadamente:
> - Imagen backend (`securescan-api`): ~4 GB (incluye Go toolchain, SecLists ~1.5 GB y nuclei-templates ~300 MB)
> - Imagen frontend (`securescan-frontend`): ~500 MB
> - Imágenes de terceros (ZAP, Metasploit, labs): ~4 GB adicionales

### 1.2 Sistema operativo

El sistema ha sido desarrollado y probado en los siguientes entornos:

| SO | Versión | Estado |
|---|---|---|
| Kali Linux | 2024.x en VirtualBox | ✅ Entorno principal de desarrollo |
| Ubuntu | 24.04 LTS | ✅ Compatible |
| Debian | 12 (Bookworm) | ✅ Compatible |
| macOS | 13+ con Docker Desktop | ⚠ Compatible (sin soporte NET_RAW para nmap) |
| Windows | 11 + WSL2 + Docker Desktop | ⚠ Compatible con limitaciones |

> **ARM (Apple Silicon / Raspberry Pi):** No compatible. Las imágenes de Metasploit y algunas herramientas Go no tienen builds oficiales para arm64.

---

## 2. PREREQUISITOS DE SOFTWARE

### 2.1 Docker Engine (versión plugin v2)

SecureScan Pro usa exclusivamente `docker compose` (con espacio, plugin v2). **No** usa `docker-compose` (con guión, v1 standalone). Verificar:

```bash
docker --version
# Docker version 26.x.x o superior

docker compose version
# Docker Compose version v2.x.x o superior
```

**Instalación en Kali Linux / Debian / Ubuntu:**

```bash
# Eliminar versiones antiguas si existen
sudo apt-get remove -y docker docker-engine docker.io containerd runc

# Instalar dependencias
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

# Agregar repositorio oficial de Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# En Kali Linux (basado en Debian)
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/debian bookworm stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io \
                        docker-buildx-plugin docker-compose-plugin

# Habilitar Docker al inicio
sudo systemctl enable docker
sudo systemctl start docker
```

**Agregar el usuario actual al grupo docker (evita usar sudo):**

```bash
sudo usermod -aG docker $USER
newgrp docker        # Aplica el cambio sin reiniciar sesión

# Verificar que funciona sin sudo
docker run --rm hello-world
```

### 2.2 Git

```bash
# Verificar
git --version   # git version 2.x.x

# Instalar si no está
sudo apt-get install -y git
```

### 2.3 pnpm (solo para desarrollo local del frontend)

> **No requerido para el despliegue con Docker.** Solo necesario si se quiere correr el frontend localmente fuera del container.

```bash
# Instalar Node.js 20 LTS primero
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Habilitar pnpm con corepack
sudo corepack enable
corepack prepare pnpm@8.15.0 --activate

# Verificar
node --version   # v20.x.x
pnpm --version   # 8.15.0
```

### 2.4 curl (para verificación)

Normalmente preinstalado. Verificar:

```bash
curl --version   # curl 7.x.x o superior
```

---

## 3. OBTENCIÓN DEL CÓDIGO FUENTE

### 3.1 Desde el archivo ZIP (distribución del proyecto SENA)

```bash
# Descomprimir el archivo del proyecto
unzip SecureScan.zip -d ~/SecureScan-main
cd ~/SecureScan-main

# Verificar la estructura
ls -la
# Debe mostrar: server/ app/ components/ lib/ docker-compose.yml start.sh verify.sh ...
```

### 3.2 Desde repositorio Git (si está disponible)

```bash
git clone <URL_DEL_REPOSITORIO> SecureScan-main
cd SecureScan-main
```

### 3.3 Verificación de integridad de la estructura

Antes de proceder, verificar que los archivos críticos existen:

```bash
# Archivos que DEBEN existir para el despliegue
ls docker-compose.yml Dockerfile.frontend start.sh verify.sh .env.example
ls server/app.py server/Dockerfile server/requirements.txt server/entrypoint.sh
ls server/modules/orchestrator.py server/modules/injection_scanner.py
ls server/utils/reporter.py server/utils/scoring.py
ls app/scanner/page.tsx lib/api-client.ts components/results-dashboard.tsx

echo "✓ Estructura verificada"
```

---

## 4. CONFIGURACIÓN DE VARIABLES DE ENTORNO (.env)

### 4.1 Creación del archivo .env

```bash
# Copiar la plantilla
cp .env.example .env

# Abrir para editar
nano .env   # o: vim .env / code .env
```

### 4.2 Variables críticas que DEBEN cambiarse antes de cualquier uso

#### SECRET_KEY — Clave secreta de Flask

La aplicación valida en arranque que `SECRET_KEY` no contenga las cadenas `"CAMBIA"` ni `"change"` cuando `FLASK_ENV != development`. Si las contiene en modo producción, lanza `RuntimeError` y no arranca.

```bash
# Generar una clave segura
openssl rand -hex 32
# Ejemplo de salida: a3f8b2c1d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1

# En .env:
SECRET_KEY=a3f8b2c1d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1
```

#### REDIS_PASSWORD — Contraseña de Redis

```bash
openssl rand -hex 16
# En .env (cambiar en ambas variables):
REDIS_URL=redis://:tu-password-aqui@redis:6379/0
REDIS_PASSWORD=tu-password-aqui
```

#### ZAP_API_KEY — Clave de autenticación de OWASP ZAP

```bash
openssl rand -hex 16
# En .env:
ZAP_API_KEY=tu-zap-key-aqui
```

#### MSF_PASSWORD — Contraseña del daemon Metasploit

```bash
# En .env:
MSF_PASSWORD=tu-msf-password-aqui
```

### 4.3 Contenido completo del .env para laboratorio SENA

Este es el archivo `.env` de referencia para el entorno educativo. Para producción expuesta a Internet, todas las contraseñas deben ser más fuertes:

```env
# ── Backend ──────────────────────────────────────────────────────────
FLASK_ENV=development
FLASK_DEBUG=0
PORT=5000

# Genera con: openssl rand -hex 32
SECRET_KEY=change-this-in-production-generate-random-key

# ── Redis ─────────────────────────────────────────────────────────────
REDIS_URL=redis://:changeme-redis-password@redis:6379/0
REDIS_PASSWORD=changeme-redis-password

# ── ZAP ───────────────────────────────────────────────────────────────
ZAP_API_URL=http://localhost:8080
ZAP_API_KEY=securescan-dev-key-2024

# ── DVWA / MariaDB ────────────────────────────────────────────────────
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=dvwa
MYSQL_USER=dvwa
MYSQL_PASSWORD=p@ssw0rd

# ── Labs ──────────────────────────────────────────────────────────────
ALLOWED_LAB_TARGETS=juice-shop:3000,dvwa:80,webgoat:8080
RESTRICT_TO_LAB_TARGETS=false

# ── Metasploit ────────────────────────────────────────────────────────
MSF_HOST=msfrpcd
MSF_PORT=55553
MSF_PASSWORD=msf

# ── API Token (vacío = sin autenticación — útil para lab) ─────────────
API_TOKEN=

# ── Frontend (Next.js) ────────────────────────────────────────────────
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_API_TOKEN=

# ── CORS ──────────────────────────────────────────────────────────────
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://frontend:3000

# ── Timeouts (segundos) ───────────────────────────────────────────────
SCAN_TIMEOUT_ZAP=1200
SCAN_TIMEOUT_NMAP=300
SCAN_TIMEOUT_GOBUSTER=300
SCAN_TIMEOUT_NUCLEI=1200
SCAN_TIMEOUT_SQLMAP=600
SCAN_TIMEOUT_PATATOR=180
SCAN_TIMEOUT_FFUF=300
SCAN_TIMEOUT_WAPPALYZER=60
SCAN_TIMEOUT_SEARCHSPLOIT=120
SCAN_TIMEOUT_METASPLOIT=900
GUNICORN_TIMEOUT=3600

# ── Logging ───────────────────────────────────────────────────────────
LOG_LEVEL=INFO
```

> **IMPORTANTE:** El archivo `.env` está en `.gitignore` y nunca debe commitearse al repositorio. Solo `.env.example` (sin valores reales) se commitea.

---

## 5. DESPLIEGUE AUTOMÁTICO CON start.sh (MÉTODO RECOMENDADO)

`start.sh` automatiza todo el proceso de build y arranque en el orden correcto. Es el método recomendado para el laboratorio SENA.

### 5.1 Ejecución

```bash
# Desde el directorio raíz del proyecto
cd ~/SecureScan-main

# Dar permisos de ejecución (solo la primera vez)
chmod +x start.sh verify.sh fix_frontend_dvwa.sh

# Ejecutar
bash start.sh
```

### 5.2 Qué hace start.sh paso a paso

```
Paso 1 — Prerrequisitos
  ├── Verifica que docker esté disponible
  └── Verifica que docker compose v2 esté disponible

Paso 2 — Configuración
  ├── Si no existe .env → copia .env.example a .env (con advertencia)
  └── Si ya existe .env → lo usa tal cual

Paso 3 — Build de imágenes
  ├── docker compose build api sqlmapapi
  │     └── Construye server/Dockerfile (~5-15 min primera vez)
  │         Descarga: Go 1.22.5, SQLMap, gobuster, ffuf, nuclei,
  │         SecLists, ExploitDB, nuclei-templates
  └── docker compose build frontend
        └── Construye Dockerfile.frontend (~2-5 min primera vez)
            Ejecuta: pnpm install + pnpm build (Next.js)

Paso 4 — Arranque secuencial
  ├── 1/5: Redis → espera PONG antes de continuar
  ├── 2/5: ZAP → en background (puede tardar ~60s en estar listo)
  ├── 3/5: dvwa-db → sleep 5s → dvwa + webgoat + juice-shop
  ├── 4/5: msfrpcd → en background (puede tardar ~2-5 min)
  └── 5/5: api + sqlmapapi → sleep 10s → frontend

Paso 5 — Verificación
  └── Polling a http://localhost:5000/api/health
      cada 3 segundos, máximo 60 intentos
      Si responde: muestra resumen de URLs y comandos útiles
      Si no responde en 60s: muestra error con comando de diagnóstico
```

### 5.3 Salida esperada de start.sh

```
═══ SecureScan Pro v3.0 — Inicio ═══

═══ Verificando prerrequisitos ═══
  ✓ Docker 26.1.3
  ✓ Docker Compose v2.27.0

═══ Configuración ═══
  ⚠ .env creado desde .env.example — revisa los valores antes de producción

═══ Construyendo imágenes ═══
[SecureScan] Construyendo backend API...
[+] Building 487.3s (23/23) FINISHED
[SecureScan] Construyendo frontend...
[+] Building 142.1s (12/12) FINISHED
  ✓ Build completado

═══ Arrancando servicios ═══
[SecureScan] 1/5 Redis...
  ✓ Redis listo
[SecureScan] 2/5 ZAP (en background — puede tardar ~60s)...
  ✓ ZAP iniciando
[SecureScan] 3/5 Labs de seguridad...
  ✓ Labs iniciando
[SecureScan] 4/5 Metasploit (en background — puede tardar ~2min)...
  ✓ Metasploit iniciando
[SecureScan] 5/5 Backend API y Frontend...
  ✓ API y Frontend iniciados

═══ Verificando estado ═══
[SecureScan] Esperando que la API esté lista (máx 60s)...
  ✓ API respondiendo en 12s

════════════════════════════════════════
  SecureScan Pro — Todo listo 🚀
════════════════════════════════════════

  Frontend:    http://localhost:3000
  API:         http://localhost:5000/api/health
  Juice Shop:  http://localhost:3001
  DVWA:        http://localhost:3002
  WebGoat:     http://localhost:3003

  Comandos útiles:
    docker compose logs -f api      # Logs del backend
    docker compose logs -f frontend # Logs del frontend
    docker compose down             # Parar todo
    bash verify.sh                  # Verificar estado
```

### 5.4 Tiempos esperados de start.sh

| Situación | Tiempo total aproximado |
|---|---|
| Primera ejecución (build + descarga de imágenes) | 15-30 minutos |
| Ejecuciones posteriores (imágenes ya construidas) | 2-4 minutos |
| Solo arranque (sin rebuild) | 1-2 minutos |

> El tiempo de la primera ejecución depende principalmente de la velocidad de la conexión a Internet, ya que se descargan SecLists (~1.5 GB), nuclei-templates (~300 MB), ExploitDB (~200 MB) y la imagen de Metasploit Framework (~1.5 GB).

---

## 6. DESPLIEGUE MANUAL PASO A PASO

Para mayor control o diagnóstico, se puede desplegar el sistema manualmente:

### 6.1 Build de las imágenes

```bash
cd ~/SecureScan-main

# Build del backend (y sqlmapapi que usa la misma imagen)
docker compose build api

# Build del frontend
docker compose build frontend

# Ver imágenes construidas
docker images | grep securescan
```

### 6.2 Arranque de Redis (primer servicio obligatorio)

```bash
docker compose up -d redis

# Esperar a que Redis esté listo
until docker compose exec redis \
    redis-cli -a "${REDIS_PASSWORD:-changeme-redis-password}" ping \
    2>/dev/null | grep -q PONG; do
  echo "Esperando Redis..."
  sleep 2
done
echo "Redis listo"
```

### 6.3 Arranque de OWASP ZAP

```bash
docker compose up -d zap

# ZAP necesita ~60 segundos para arrancar completamente
# Verificar cuando esté listo:
until curl -sf "http://localhost:8080/JSON/core/view/version/?apikey=${ZAP_API_KEY:-securescan-dev-key-2024}" \
    | grep -q "version"; do
  echo "Esperando ZAP..."
  sleep 5
done
echo "ZAP listo"
```

### 6.4 Arranque de la base de datos DVWA

```bash
# DVWA depende de MariaDB — arrancar la DB primero
docker compose up -d dvwa-db

# Esperar a que MariaDB esté lista (health check cada 10s, start_period 30s)
sleep 35
echo "MariaDB lista"
```

### 6.5 Arranque de los laboratorios

```bash
docker compose up -d dvwa webgoat juice-shop

# Los labs pueden tardar 30-60s en arrancar
# Verificar individualmente:
until curl -sf -o /dev/null -L http://localhost:3002; do
  echo "Esperando DVWA..."
  sleep 5
done
echo "DVWA listo"

until curl -sf -o /dev/null http://localhost:3001; do
  echo "Esperando Juice Shop..."
  sleep 5
done
echo "Juice Shop listo"

until curl -sf -o /dev/null http://localhost:3003/WebGoat/; do
  echo "Esperando WebGoat..."
  sleep 5
done
echo "WebGoat listo"
```

### 6.6 Arranque de Metasploit

```bash
# Metasploit puede tardar entre 2 y 5 minutos en arrancar
docker compose up -d msfrpcd
echo "Metasploit iniciando en background (puede tardar hasta 5 min)..."
```

### 6.7 Arranque del backend API y SQLMap API

```bash
docker compose up -d api sqlmapapi

# Esperar al health check del API (start_period 30s)
until curl -sf http://localhost:5000/api/health | grep -q healthy; do
  echo "Esperando API..."
  sleep 5
done
echo "API lista"
```

### 6.8 Arranque del frontend

```bash
docker compose up -d frontend

# Esperar al health check del frontend (start_period 30s)
until curl -sf -o /dev/null http://localhost:3000; do
  echo "Esperando Frontend..."
  sleep 5
done
echo "Frontend listo"
```

### 6.9 Verificar estado completo

```bash
docker compose ps
```

La salida esperada muestra todos los servicios con estado `healthy` o `running`:

```
NAME                     IMAGE                          STATUS                   PORTS
dvwa                     ghcr.io/digininja/dvwa:latest  Up (healthy)             0.0.0.0:3002->80/tcp
dvwa-db                  mariadb:10.11                  Up (healthy)
juice-shop               bkimminich/juice-shop:v17.0.0  Up (healthy)             0.0.0.0:3001->3000/tcp
securescan-api           securescan-main-api            Up (healthy)             0.0.0.0:5000->5000/tcp
securescan-frontend      securescan-main-frontend       Up (healthy)             0.0.0.0:3000->3000/tcp
securescan-msfrpcd       metasploitframework/...        Up                       0.0.0.0:55553->55553/tcp
securescan-redis         redis:7-alpine                 Up (healthy)             127.0.0.1:6379->6379/tcp
securescan-sqlmapapi     securescan-main-api            Up (healthy)             127.0.0.1:8775->8775/tcp
securescan-zap           ghcr.io/zaproxy/zaproxy:stable Up (healthy)             0.0.0.0:8080->8080/tcp
webgoat                  webgoat/webgoat:latest         Up (healthy)             0.0.0.0:3003->8080/tcp
```

---

## 7. VERIFICACIÓN DEL DESPLIEGUE

### 7.1 Script de verificación automática

```bash
bash verify.sh
```

**Salida esperada cuando todo está correcto:**

```
═══ SecureScan Pro v3.0 — Verificación ═══

── Contenedores ──
  ✓ securescan-api
  ✓ securescan-frontend
  ✓ securescan-redis
  ✓ securescan-zap
  ✓ securescan-sqlmapapi
  ✓ juice-shop
  ✓ dvwa
  ✓ webgoat
  ✓ msfrpcd

── Backend API ──
  ✓ Health endpoint
  ✓ Config endpoint
  ✓ History endpoint

── Frontend ──
  ✓ Frontend en :3000

── Labs ──
  ✓ Juice Shop :3001
  ✓ DVWA :3002
  ✓ WebGoat :3003

── ZAP ──
  ✓ ZAP API :8080

── Herramientas dentro del contenedor API ──
  ✓ nmap
  ✓ searchsploit
  ✓ nuclei
  ✓ sqlmap
  ✓ patator
  ✓ ffuf
  ✓ gobuster
  ✓ wkhtmltopdf

── Redis ──
  ✓ Redis ping

══ Resultado: 22 ✓  0 ✗ ══
🟢 Todo OK — SecureScan Pro listo para usar
```

### 7.2 Verificación manual de endpoints críticos

```bash
# Health check general
curl -s http://localhost:5000/api/health | python3 -m json.tool

# Respuesta esperada:
# {
#   "status": "healthy",
#   "version": "5.0.0",
#   "storage": "connected",
#   "zap_configured": true,
#   "tools": ["wappalyzer", "nmap", "gobuster", "zap", ...]
# }

# Configuración del sistema
curl -s http://localhost:5000/api/config | python3 -m json.tool

# Historial (vacío al inicio)
curl -s http://localhost:5000/api/history | python3 -m json.tool
```

### 7.3 Verificación de herramientas dentro del container API

```bash
# Verificar todas las herramientas de seguridad instaladas
docker compose exec api bash -c "
  echo '── Herramientas de seguridad ──'
  for tool in nmap nuclei gobuster ffuf sqlmap patator searchsploit wkhtmltopdf; do
    if which \$tool > /dev/null 2>&1; then
      echo \"  ✓ \$tool: \$(which \$tool)\"
    else
      echo \"  ✗ \$tool: NO ENCONTRADO\"
    fi
  done
  echo ''
  echo '── Versiones ──'
  nmap --version | head -1
  nuclei -version 2>&1 | head -1
  gobuster version 2>&1 | head -1
  ffuf -V 2>&1 | head -1
  sqlmap --version 2>&1 | head -1
"
```

### 7.4 Verificación de conectividad entre servicios

```bash
# Verificar que la API puede alcanzar ZAP
docker compose exec api curl -sf \
  "http://zap:8080/JSON/core/view/version/?apikey=${ZAP_API_KEY:-securescan-dev-key-2024}" \
  | python3 -m json.tool

# Verificar que la API puede alcanzar los labs
docker compose exec api curl -sf -o /dev/null -w "%{http_code}" http://juice-shop:3000
docker compose exec api curl -sf -o /dev/null -w "%{http_code}" http://dvwa:80
docker compose exec api curl -sf -o /dev/null -w "%{http_code}" http://webgoat:8080/WebGoat/

# Verificar que la API puede alcanzar Redis
docker compose exec api python3 -c "
import redis, os
r = redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379/0'), decode_responses=True)
print('Redis ping:', r.ping())
"
```

---

## 8. TIEMPOS DE ARRANQUE POR SERVICIO

Tiempos medidos desde `docker compose up -d <servicio>` hasta que el health check pasa:

| Servicio | start_period | Tiempo real típico | Notas |
|---|---|---|---|
| `redis` | Inmediato | 3-5 s | Muy rápido, imagen alpine |
| `dvwa-db` | 30 s | 20-35 s | MariaDB inicialización |
| `juice-shop` | 60 s | 30-45 s | Node.js startup |
| `dvwa` | 45 s | 30-60 s | Depende de dvwa-db |
| `webgoat` | 60 s | 45-90 s | Java Spring Boot, es el más lento de los labs |
| `sqlmapapi` | 20 s | 10-15 s | Python startup rápido |
| `zap` | 60 s | 45-90 s | JVM + carga de reglas |
| `api` | 30 s | 15-25 s | Flask + Gunicorn |
| `frontend` | 30 s | 20-40 s | Next.js server.js |
| `msfrpcd` | 120 s | 120-300 s | Metasploit tarda más — no bloquea la API |

> **msfrpcd:** Metasploit Framework puede tardar entre 2 y 5 minutos en estar completamente operativo. El docker-compose.yml configura su dependencia como `service_started` (no `service_healthy`) para que la API no espere a Metasploit antes de arrancar. Si un escaneo usa Metasploit antes de que haya terminado de arrancar, el módulo activará automáticamente el modo simulación.

---

## 9. MAPA DE PUERTOS Y URLS DE ACCESO

### 9.1 Puertos expuestos al host

| Servicio | Puerto host | Puerto container | Protocolo | Acceso |
|---|---|---|---|---|
| Frontend (Next.js) | `3000` | `3000` | HTTP | `http://localhost:3000` |
| Backend API (Flask) | `5000` | `5000` | HTTP | `http://localhost:5000` |
| OWASP ZAP | `8080` | `8080` | HTTP | `http://localhost:8080` |
| Metasploit RPC | `55553` | `55553` | TCP/RPC | Solo API interna |
| Juice Shop | `3001` | `3000` | HTTP | `http://localhost:3001` |
| DVWA | `3002` | `80` | HTTP | `http://localhost:3002` |
| WebGoat | `3003` | `8080` | HTTP | `http://localhost:3003/WebGoat/` |
| Redis | `127.0.0.1:6379` | `6379` | TCP | Solo localhost |
| SQLMap API | `127.0.0.1:8775` | `8775` | HTTP | Solo localhost |

> **Redis y SQLMap API** están mapeados solo a `127.0.0.1` (no `0.0.0.0`) por seguridad. Solo son accesibles desde el host local, no desde otras máquinas en la red.

### 9.2 URLs de acceso rápido

| Aplicación | URL |
|---|---|
| SecureScan Pro Frontend | http://localhost:3000 |
| SecureScan Pro API Health | http://localhost:5000/api/health |
| SecureScan Pro API Config | http://localhost:5000/api/config |
| OWASP Juice Shop | http://localhost:3001 |
| DVWA | http://localhost:3002 |
| DVWA Setup (primera vez) | http://localhost:3002/setup.php |
| WebGoat | http://localhost:3003/WebGoat/ |
| ZAP Web UI (local) | http://localhost:8080 |

### 9.3 Hostnames internos Docker (entre containers)

Los servicios se comunican entre sí por hostname dentro de las redes Docker. Estos hostnames NO son accesibles desde el host:

| Container | Hostname interno | Puerto interno |
|---|---|---|
| `securescan-api` | `api` | `5000` |
| `securescan-redis` | `redis` | `6379` |
| `securescan-zap` | `zap` | `8080` |
| `securescan-sqlmapapi` | `sqlmapapi` | `8775` |
| `securescan-msfrpcd` | `msfrpcd` | `55553` |
| `juice-shop` | `juice-shop` | `3000` |
| `dvwa` | `dvwa` | `80` |
| `dvwa-db` | `dvwa-db` | `3306` |
| `webgoat` | `webgoat` | `8080` |

---

## 10. CREDENCIALES DEL LABORATORIO

### 10.1 Credenciales de los targets vulnerables

| Target | URL | Usuario | Contraseña | Notas |
|---|---|---|---|---|
| DVWA | http://localhost:3002 | `admin` | `password` | Nivel de seguridad forzado a `low` por auto-login |
| Juice Shop | http://localhost:3001 | `admin@juice-sh.op` | `admin123` | JWT token via REST API |
| WebGoat | http://localhost:3003/WebGoat/ | `securescan` | `Password` | Spring Security — GET inicial obligatorio |

### 10.2 Credenciales de infraestructura

| Servicio | Variable | Valor por defecto (.env.example) |
|---|---|---|
| Redis | `REDIS_PASSWORD` | `changeme-redis-password` |
| DVWA / MariaDB root | `MYSQL_ROOT_PASSWORD` | `rootpassword` |
| DVWA / MariaDB user | `MYSQL_PASSWORD` | `p@ssw0rd` |
| Metasploit RPC | `MSF_PASSWORD` | `msf` |
| ZAP API | `ZAP_API_KEY` | `securescan-dev-key-2024` |
| Flask Secret | `SECRET_KEY` | `change-this-in-production-generate-random-key` |

> **Importante:** En el entorno de laboratorio SENA estas credenciales por defecto son aceptables. Para cualquier exposición a redes externas, todas deben ser cambiadas por valores generados con `openssl rand -hex 32`.

### 10.3 Auto-login implementado en el sistema

SecureScan Pro realiza auto-login automático antes de cada escaneo. El proceso específico por laboratorio es:

**DVWA (3 peticiones secuenciales):**
```
1. GET  http://dvwa:80/login.php              → obtener CSRF token del login
2. POST http://dvwa:80/login.php              → enviar credenciales + token → obtener PHPSESSID
3. GET  http://dvwa:80/security.php           → obtener CSRF token de security.php
4. POST http://dvwa:80/security.php           → establecer security=low con token correcto
   Cookie resultante: PHPSESSID=...; security=low
```

**Juice Shop (1 petición):**
```
POST http://juice-shop:3000/rest/user/login   → JSON con email + password
   Respuesta: { "authentication": { "token": "JWT..." } }
   Cookie resultante: Bearer JWT token en cabecera Authorization
```

**WebGoat (2 peticiones):**
```
1. GET  http://webgoat:8080/WebGoat/login     → obtener cookie inicial de sesión
2. POST http://webgoat:8080/WebGoat/login     → enviar credenciales
   Cookie resultante: JSESSIONID=...
```

---

## 11. OPERACIÓN DIARIA — COMANDOS ESENCIALES

### 11.1 Iniciar la plataforma

```bash
# Método recomendado (automático)
bash start.sh

# Método manual (solo arrancar sin rebuild)
docker compose up -d

# Arrancar solo algunos servicios
docker compose up -d api frontend redis
```

### 11.2 Detener la plataforma

```bash
# Parar todos los servicios (conserva datos en volúmenes)
docker compose down

# Parar y eliminar volúmenes (BORRA TODOS LOS DATOS)
docker compose down -v

# Parar un servicio específico
docker compose stop api
docker compose stop frontend
```

### 11.3 Reiniciar servicios

```bash
# Reiniciar un servicio sin rebuild
docker compose restart api
docker compose restart frontend
docker compose restart redis

# Reiniciar todos los servicios
docker compose restart

# Reiniciar solo los labs
docker compose restart dvwa webgoat juice-shop
```

### 11.4 Rebuild tras cambios en el código

```bash
# Rebuild del backend (tras cambios en server/)
docker compose build api
docker compose up -d --no-deps api

# Rebuild del frontend (tras cambios en app/, components/, lib/)
docker compose build frontend
docker compose up -d --no-deps frontend

# Rebuild completo de todas las imágenes propias
docker compose build
docker compose up -d

# Forzar rebuild sin cache (resolver problemas extraños)
docker compose build --no-cache api
docker compose build --no-cache frontend
```

### 11.5 Ejecutar comandos dentro de los containers

```bash
# Abrir shell en el container de la API
docker compose exec api bash

# Ejecutar un comando puntual en la API
docker compose exec api nmap --version
docker compose exec api nuclei -version
docker compose exec api python3 -c "import flask; print(flask.__version__)"

# Abrir shell en el container de la base de datos DVWA
docker compose exec dvwa-db bash

# Acceder a MySQL/MariaDB de DVWA
docker compose exec dvwa-db mariadb -u dvwa -p"p@ssw0rd" dvwa
```

### 11.6 Estado del sistema

```bash
# Ver todos los containers con su estado
docker compose ps

# Ver uso de recursos en tiempo real
docker stats

# Ver uso de recursos con nombres amigables
docker stats $(docker compose ps -q)

# Ver el estado de los health checks
docker inspect securescan-api | python3 -c "
import json, sys
data = json.load(sys.stdin)
hc = data[0].get('State', {}).get('Health', {})
print('Status:', hc.get('Status'))
for log in hc.get('Log', [])[-3:]:
    print('Output:', log.get('Output', '').strip())
"
```

---

## 12. GESTIÓN DE LOGS

### 12.1 Ver logs en tiempo real

```bash
# Logs de todos los servicios
docker compose logs -f

# Logs del backend API (más útil para depurar escaneos)
docker compose logs -f api

# Logs del frontend Next.js
docker compose logs -f frontend

# Logs de ZAP
docker compose logs -f zap

# Logs de Metasploit
docker compose logs -f msfrpcd

# Logs de DVWA y su base de datos
docker compose logs -f dvwa dvwa-db
```

### 12.2 Opciones útiles de logs

```bash
# Últimas N líneas de un servicio
docker compose logs --tail=50 api

# Logs desde una fecha específica
docker compose logs --since="2026-06-05T10:00:00" api

# Logs con timestamps
docker compose logs -f -t api

# Logs de múltiples servicios simultáneamente
docker compose logs -f api zap
```

### 12.3 Interpretar logs del backend API

Los logs del backend (`docker compose logs -f api`) muestran el flujo completo de cada escaneo. Ejemplo anotado:

```log
# Arranque de Gunicorn
2026-06-05 10:00:00 [1] [INFO] Starting gunicorn 21.2.0
2026-06-05 10:00:00 [1] [INFO] Listening at: http://0.0.0.0:5000 (1)
2026-06-05 10:00:00 [1] [INFO] Worker with pid 8 booted.

# Inicio de escaneo
2026-06-05 10:05:00 INFO - POST /api/scan — target: http://juice-shop:3000
2026-06-05 10:05:01 INFO - Scan iniciado: job_id=550e8400-e29b-41d4-a716-446655440000

# Progreso del pipeline (uno por cada herramienta)
2026-06-05 10:05:02 INFO - [550e...] Paso 1: Wappalyzer — iniciando
2026-06-05 10:05:15 INFO - [550e...] Paso 1: Wappalyzer — completado (13s)
2026-06-05 10:05:15 INFO - [550e...] Paso 2: Nmap — iniciando
...

# Finalización
2026-06-05 10:35:00 INFO - [550e...] Scan completado. Score: 65/100 (D+)
```

> **Warnings habituales que son normales:**
> - `API_TOKEN no configurado` — normal en lab sin autenticación configurada.
> - `Usando SECRET_KEY de desarrollo` — normal cuando `FLASK_ENV=development`.
> - `wappalyzer-cli no disponible — usando librería Python` — comportamiento esperado.
> - `Metasploit no disponible — usando simulación` — si msfrpcd aún está arrancando.

---

## 13. GESTIÓN DE VOLÚMENES Y DATOS PERSISTENTES

### 13.1 Listar volúmenes creados

```bash
docker volume ls | grep securescan
```

Salida esperada:
```
local     securescan-main_redis-data
local     securescan-main_scan-reports
local     securescan-main_dvwa-db-data
local     securescan-main_msf-data
local     securescan-main_nuclei-templates
local     securescan-main_juice-shop-data
local     securescan-main_webgoat-data
```

### 13.2 Acceder a los reportes generados

Los reportes se guardan en el volumen `scan-reports` montado en `/app/reports` dentro del container API:

```bash
# Listar reportes desde el container
docker compose exec api ls /app/reports/

# Copiar todos los reportes al host
docker cp securescan-api:/app/reports/ ./reportes-backup/

# Copiar un reporte específico
docker cp securescan-api:/app/reports/report-<scan_id>.html ./reporte.html

# Ver el tamaño total de los reportes
docker compose exec api du -sh /app/reports/
```

### 13.3 Limpiar datos

```bash
# Limpiar solo los reportes generados (sin borrar otros datos)
docker compose exec api rm -f /app/reports/report-*.html \
                              /app/reports/report-*.pdf \
                              /app/reports/report-*.json \
                              /app/reports/report-*.csv

# Limpiar historial de Redis (todos los scans guardados)
docker compose exec redis \
  redis-cli -a "${REDIS_PASSWORD:-changeme-redis-password}" FLUSHDB

# Limpiar DVWA y reinicializar su base de datos
docker compose down dvwa dvwa-db
docker volume rm securescan-main_dvwa-db-data
docker compose up -d dvwa-db
sleep 35
docker compose up -d dvwa
# Luego visitar http://localhost:3002/setup.php para reinicializar

# Eliminar TODO (containers + volúmenes + datos) — IRREVERSIBLE
docker compose down -v
docker system prune -f
```

### 13.4 Respaldo del estado de Redis

```bash
# Forzar un BGSAVE en Redis para persistir el estado
docker compose exec redis \
  redis-cli -a "${REDIS_PASSWORD:-changeme-redis-password}" BGSAVE

# Copiar el archivo de datos de Redis al host
docker cp securescan-redis:/data/dump.rdb ./redis-backup-$(date +%Y%m%d).rdb
```

---

## 14. ACTUALIZACIÓN DEL SISTEMA

### 14.1 Actualizar el código fuente

```bash
# Si el proyecto está en Git
git pull origin main

# Si se distribuye por ZIP, descomprimir y reemplazar
```

### 14.2 Rebuild de imágenes tras actualización de código

```bash
# Rebuild solo del backend (si cambiaron archivos en server/)
docker compose build --no-cache api
docker compose up -d --no-deps api

# Rebuild solo del frontend (si cambiaron archivos en app/, components/, lib/)
docker compose build --no-cache frontend
docker compose up -d --no-deps frontend
```

### 14.3 Actualizar imágenes de terceros (labs, ZAP, etc.)

```bash
# Descargar versiones más recientes de las imágenes
docker compose pull zap
docker compose pull juice-shop
docker compose pull webgoat

# Reiniciar con las imágenes actualizadas
docker compose up -d --force-recreate zap
docker compose up -d --force-recreate juice-shop webgoat
```

### 14.4 Actualizar templates de Nuclei

Las plantillas de Nuclei se actualizan automáticamente a través del volumen `nuclei-templates`. Para forzar una actualización manual:

```bash
docker compose exec api nuclei -update-templates
```

---

## 15. DESARROLLO LOCAL (SIN DOCKER)

Para desarrollo activo en el frontend o backend sin necesidad de reconstruir las imágenes Docker completas.

### 15.1 Backend Flask en local (modo desarrollo)

```bash
cd ~/SecureScan-main/server

# Crear entorno virtual Python
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno mínimas para desarrollo
export FLASK_ENV=development
export FLASK_DEBUG=1
export SECRET_KEY=dev-key-for-local-testing-only
export REDIS_URL=redis://localhost:6379/0    # Redis debe estar corriendo en Docker
export ZAP_API_URL=http://localhost:8080     # ZAP debe estar corriendo en Docker

# Iniciar Flask en modo desarrollo (auto-reload)
python3 app.py
# o:
flask run --host=0.0.0.0 --port=5000
```

> **Nota:** Para el modo de desarrollo local del backend, los containers de Redis, ZAP y los labs deben seguir corriendo en Docker. Solo el proceso de Flask se corre localmente.

### 15.2 Frontend Next.js en local (modo desarrollo)

```bash
cd ~/SecureScan-main

# Instalar dependencias (primera vez)
pnpm install

# Configurar variables de entorno del frontend
# Crear .env.local (no .env — ese es para Docker)
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_API_TOKEN=
BACKEND_URL=http://localhost:5000
EOF

# Iniciar en modo desarrollo (hot reload)
pnpm dev
# Frontend disponible en: http://localhost:3000
```

### 15.3 Verificar tipos TypeScript

```bash
cd ~/SecureScan-main
pnpm type-check   # tsc --noEmit
```

### 15.4 Ejecutar linter

```bash
cd ~/SecureScan-main
pnpm lint         # ESLint con config Next.js
pnpm lint:fix     # Auto-corrección
```

### 15.5 Generar build de producción del frontend

```bash
cd ~/SecureScan-main
pnpm build        # Genera .next/
pnpm start        # Sirve el build de producción en puerto 3000
```

---

## 16. TROUBLESHOOTING — PROBLEMAS FRECUENTES Y SOLUCIONES

### 16.1 La API no arranca — "SECRET_KEY debe ser una clave segura"

**Síntoma:**
```log
RuntimeError: SECRET_KEY debe ser una clave segura en producción.
```

**Causa:** La variable `SECRET_KEY` en `.env` contiene la cadena `"change"` o `"CAMBIA"` y `FLASK_ENV` no es `"development"`.

**Solución:**
```bash
# Opción A: cambiar FLASK_ENV a development (para laboratorio)
sed -i 's/FLASK_ENV=production/FLASK_ENV=development/' .env
docker compose restart api

# Opción B: generar una clave nueva (para producción)
NEW_KEY=$(openssl rand -hex 32)
sed -i "s/^SECRET_KEY=.*/SECRET_KEY=$NEW_KEY/" .env
docker compose restart api
```

### 16.2 DVWA no responde o muestra error de base de datos

**Síntoma:** `http://localhost:3002` no carga o muestra error de conexión MySQL.

**Causa más común:** `dvwa-db` no terminó de inicializarse antes de que `dvwa` intentara conectarse.

**Solución:**
```bash
# Usar el script de reparación automático
bash fix_frontend_dvwa.sh

# O manualmente:
docker compose restart dvwa-db
sleep 30
docker compose restart dvwa
sleep 10

# Si persiste — inicializar la base de datos manualmente
curl -sf -o /dev/null -L "http://localhost:3002/setup.php?initdb=true" || true
sleep 3
curl -sf -L http://localhost:3002 | grep -i "login\|dvwa"
```

### 16.3 El frontend no carga — Puerto 3000 no responde

**Síntoma:** `http://localhost:3000` no carga o muestra error de conexión.

**Causa:** El build del frontend falló silenciosamente o el container no arrancó.

**Solución:**
```bash
# Ver qué pasó durante el build
docker compose logs --tail=50 frontend

# Reparar con el script automático
bash fix_frontend_dvwa.sh

# O manualmente:
docker compose rm -sf frontend
docker compose build --no-cache frontend
docker compose up -d frontend
docker compose logs -f frontend
```

### 16.4 ZAP no responde o tarda demasiado

**Síntoma:** Los escaneos con ZAP fallan o el paso 7 se marca como error.

**Causa:** ZAP necesita ~60-90 segundos para arrancar completamente. Si un escaneo se inicia antes, ZAP no está listo.

**Solución:**
```bash
# Verificar que ZAP está funcionando
curl -sf "http://localhost:8080/JSON/core/view/version/?apikey=securescan-dev-key-2024"

# Si no responde — ver sus logs
docker compose logs --tail=30 zap

# Reiniciar ZAP
docker compose restart zap
# Esperar ~90 segundos antes de iniciar otro escaneo con ZAP
```

### 16.5 Metasploit no conecta — módulos muestran simulación

**Síntoma:** Los resultados de Metasploit muestran `"simulated": true`.

**Causa:** msfrpcd aún está arrancando (puede tardar hasta 5 minutos) o la contraseña no coincide.

**Solución:**
```bash
# Ver si msfrpcd está listo
docker compose logs --tail=20 msfrpcd
# Buscar: "msfrpcd started on port 55553" o "RPC service loaded"

# Verificar conectividad TCP al puerto RPC
docker compose exec api bash -c "echo > /dev/tcp/msfrpcd/55553 && echo 'Conectado' || echo 'No disponible'"

# Si el puerto responde pero sigue en simulación — verificar contraseña
grep MSF_PASSWORD .env
# Debe coincidir con lo que msfrpcd usó al arrancar
```

### 16.6 Redis — Fallback en memoria (almacenamiento no persistente)

**Síntoma:** La API muestra en `/api/health`: `"storage": "memory"` en lugar de `"connected"`.

**Causa:** Redis no está disponible o la contraseña no coincide.

**Solución:**
```bash
# Verificar estado de Redis
docker compose ps redis
docker compose logs redis

# Probar conexión manual
docker compose exec redis \
  redis-cli -a "${REDIS_PASSWORD:-changeme-redis-password}" ping
# Debe responder: PONG

# Si la contraseña no coincide — verificar consistencia en .env
grep -E "REDIS_URL|REDIS_PASSWORD" .env
# REDIS_URL debe contener la misma contraseña que REDIS_PASSWORD
```

### 16.7 Escaneo queda en estado "running" sin progresar

**Síntoma:** Un escaneo inicia y el progreso se congela en algún paso.

**Causa posible:** Timeout de una herramienta, error no capturado, o un paso que tarda más de lo configurado.

**Diagnóstico:**
```bash
# Ver logs del API en tiempo real
docker compose logs -f api

# Consultar el estado del scan directamente
SCAN_ID="el-uuid-del-scan-aqui"
curl -s http://localhost:5000/api/scan/$SCAN_ID/status | python3 -m json.tool

# Ver qué paso está corriendo
curl -s http://localhost:5000/api/scan/$SCAN_ID/status \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
for step in data.get('steps', []):
    print(f\"{step['status']:12} — {step['name']}\")
"
```

**Solución si está bloqueado:**
```bash
# El scan se limpiará automáticamente tras el TTL de Redis (3600s para running)
# Para limpiar manualmente:
curl -X DELETE http://localhost:5000/api/scan/$SCAN_ID
```

### 16.8 Error de permisos en nmap dentro del container

**Síntoma:** Nmap retorna error de permisos al intentar escaneos con raw sockets.

**Causa:** El container API no tiene la capacidad `NET_RAW` asignada, o el `setcap` del Dockerfile falló.

**Verificación:**
```bash
# Ver las capabilities del binario nmap
docker compose exec api getcap /usr/bin/nmap
# Debe mostrar: /usr/bin/nmap cap_net_raw,cap_net_admin=eip

# Verificar que el container tiene NET_RAW
docker inspect securescan-api | python3 -c "
import json, sys
data = json.load(sys.stdin)
caps = data[0].get('HostConfig', {}).get('CapAdd', [])
print('CapAdd:', caps)
"
# Debe incluir NET_RAW y NET_ADMIN
```

### 16.9 "docker compose" no se reconoce — usando v1 legacy

**Síntoma:** `bash: docker-compose: command not found` o `docker compose` no funciona.

**Causa:** El sistema tiene `docker-compose` v1 standalone pero no el plugin v2.

**Solución:**
```bash
# Instalar el plugin v2
sudo apt-get install -y docker-compose-plugin

# Verificar
docker compose version
# Docker Compose version v2.x.x
```

### 16.10 Build del backend muy lento o falla por timeout de red

**Síntoma:** `docker compose build api` tarda más de 30 minutos o falla con error de red.

**Causa:** Descarga de SecLists (~1.5 GB), nuclei-templates (~300 MB) o Metasploit framework.

**Solución:**
```bash
# Aumentar timeout de Docker
export DOCKER_CLIENT_TIMEOUT=300
export COMPOSE_HTTP_TIMEOUT=300

# Rebuild con más verbosidad para ver qué paso falla
docker compose build --no-cache --progress=plain api 2>&1 | tee build.log

# Si falla en un paso específico de git clone — puede ser problema de red transitorio
# Intentar de nuevo
docker compose build api
```

### 16.11 Frontend muestra "Failed to fetch" al intentar escanear

**Síntoma:** El botón de escaneo no funciona, la consola del navegador muestra `Failed to fetch` o `net::ERR_CONNECTION_REFUSED`.

**Causa:** `NEXT_PUBLIC_API_URL` no apunta correctamente al backend.

**Verificación:**
```bash
# Ver cuál URL usa el frontend
docker compose exec frontend env | grep NEXT_PUBLIC_API_URL
# Debe ser: http://localhost:5000

# Verificar que el backend responde desde el host
curl -s http://localhost:5000/api/health | grep healthy
```

**Solución:**
```bash
# Asegurarse de que .env tiene:
# NEXT_PUBLIC_API_URL=http://localhost:5000

# Rebuild del frontend con la URL correcta
docker compose build --no-cache frontend
docker compose up -d --no-deps frontend
```

---

## 17. REFERENCIA COMPLETA DE VARIABLES DE ENTORNO

### 17.1 Variables del Backend (server/app.py)

| Variable | Tipo | Default | Descripción |
|---|---|---|---|
| `FLASK_ENV` | string | `development` | Modo Flask. `development` permite SECRET_KEY débil |
| `FLASK_DEBUG` | int | `0` | `1` activa debug mode (nunca en producción) |
| `PORT` | int | `5000` | Puerto del servidor Flask |
| `SECRET_KEY` | string | *(requerido)* | Clave secreta Flask. Generar con `openssl rand -hex 32` |
| `REDIS_URL` | string | `redis://localhost:6379/0` | URL de conexión Redis con autenticación |
| `REDIS_PASSWORD` | string | `changeme-redis-password` | Contraseña Redis (usada también en el docker-compose) |
| `ZAP_API_URL` | string | `http://zap:8080` | URL del servicio ZAP (hostname interno Docker) |
| `ZAP_API_KEY` | string | `securescan-dev-key-2024` | Clave API de autenticación de ZAP |
| `SQLMAP_API_URL` | string | `http://sqlmapapi:8775` | URL de la SQLMap REST API |
| `MSF_HOST` | string | `msfrpcd` | Hostname del daemon Metasploit |
| `MSF_PORT` | int | `55553` | Puerto RPC de Metasploit |
| `MSF_PASSWORD` | string | `msf` | Contraseña RPC de Metasploit |
| `API_TOKEN` | string | `""` (vacío) | Token de autenticación. Vacío = sin autenticación |
| `ALLOWED_ORIGINS` | string | `http://localhost:3000,...` | Orígenes CORS permitidos (coma-separados) |
| `ALLOWED_LAB_TARGETS` | string | `juice-shop:3000,dvwa:80,webgoat:8080` | Targets del lab (siempre permitidos) |
| `RESTRICT_TO_LAB_TARGETS` | bool | `false` | Si `true`, solo permite targets del lab |
| `GUNICORN_TIMEOUT` | int | `3600` | Timeout de Gunicorn en segundos |
| `LOG_LEVEL` | string | `INFO` | Nivel de logging Python |
| `TZ` | string | `America/Bogota` | Zona horaria del container |

### 17.2 Timeouts por herramienta

| Variable | Default (s) | Descripción |
|---|---|---|
| `SCAN_TIMEOUT_WAPPALYZER` | `60` | Timeout fingerprinting tecnológico |
| `SCAN_TIMEOUT_NMAP` | `300` | Timeout escaneo de puertos (5 min) |
| `SCAN_TIMEOUT_FFUF` | `300` | Timeout fuzzing de endpoints (5 min) |
| `SCAN_TIMEOUT_GOBUSTER` | `300` | Timeout enumeración de directorios (5 min) |
| `SCAN_TIMEOUT_ZAP` | `1200` | Timeout DAST ZAP completo (20 min) |
| `SCAN_TIMEOUT_NUCLEI` | `1200` | Timeout escaneo de plantillas (20 min) |
| `SCAN_TIMEOUT_SQLMAP` | `600` | Timeout detección SQLi (10 min) |
| `SCAN_TIMEOUT_PATATOR` | `180` | Timeout fuerza bruta (3 min) |
| `SCAN_TIMEOUT_METASPLOIT` | `900` | Timeout módulos Metasploit (15 min) |
| `SCAN_TIMEOUT_SEARCHSPLOIT` | `120` | Timeout búsqueda exploits (2 min) |
| `SCAN_TIMEOUT_INJECTION` | `600` | Timeout InjectionScanner (10 min) |

> **`GUNICORN_TIMEOUT` debe ser mayor que el timeout más largo de cualquier herramienta.** El valor default de 3600s garantiza que ningún escaneo sea matado por Gunicorn antes de terminar.

### 17.3 Parámetros de herramientas individuales

| Variable | Default | Descripción |
|---|---|---|
| `SQLMAP_LEVEL` | `3` | Profundidad de tests SQLMap (1-5) |
| `SQLMAP_RISK` | `2` | Riesgo de payloads SQLMap (1-3) |
| `SQLMAP_THREADS` | `5` | Threads paralelos SQLMap |
| `GOBUSTER_THREADS` | `20` | Threads paralelos Gobuster |
| `GOBUSTER_DELAY_MS` | `0` | Delay entre requests Gobuster (ms) |
| `ZAP_SPIDER_MAX_CHILDREN` | `50` | Máximo de URLs hijas en el spider ZAP |

### 17.4 Variables del Frontend (Next.js — prefijo NEXT_PUBLIC_)

| Variable | Default | Descripción |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:5000` | URL base de la API para el browser |
| `NEXT_PUBLIC_API_TOKEN` | `""` (vacío) | Token de autenticación para el browser |
| `BACKEND_URL` | `http://api:5000` | URL interna Docker para SSR y rewrites |
| `NEXT_PUBLIC_APP_NAME` | `SecureScan Pro` | Nombre de la app (hardcoded en next.config.mjs) |
| `NEXT_PUBLIC_APP_VERSION` | `3.0.0` | Versión de la app (hardcoded en next.config.mjs) |

### 17.5 Variables de MariaDB (DVWA)

| Variable | Default | Descripción |
|---|---|---|
| `MYSQL_ROOT_PASSWORD` | `rootpassword` | Contraseña root de MariaDB |
| `MYSQL_DATABASE` | `dvwa` | Nombre de la base de datos DVWA |
| `MYSQL_USER` | `dvwa` | Usuario de la base de datos DVWA |
| `MYSQL_PASSWORD` | `p@ssw0rd` | Contraseña del usuario DVWA |

---

## 18. ARQUITECTURA DE REDES DOCKER

### 18.1 Redes definidas

| Red | Driver | Subnet | Propósito |
|---|---|---|---|
| `securescan-net` | bridge | `172.20.0.0/16` | Servicios de infraestructura |
| `lab-net` | bridge | `172.21.0.0/16` | Targets vulnerables aislados |

### 18.2 Membresía de servicios en redes

| Servicio | securescan-net | lab-net | Justificación |
|---|---|---|---|
| `frontend` | ✅ | ❌ | Solo necesita comunicarse con la API |
| `api` | ✅ | ✅ | Necesita alcanzar ZAP, Redis y los labs |
| `redis` | ✅ | ❌ | Solo accedido por la API |
| `zap` | ✅ | ✅ | Necesita escanear los labs directamente |
| `sqlmapapi` | ✅ | ✅ | Necesita alcanzar los labs para SQLi |
| `msfrpcd` | ✅ | ✅ | Necesita alcanzar los labs para exploits |
| `juice-shop` | ❌ | ✅ | Target aislado en lab-net |
| `dvwa` | ❌ | ✅ | Target aislado en lab-net |
| `dvwa-db` | ❌ | ✅ | Base de datos solo accesible por dvwa |
| `webgoat` | ❌ | ✅ | Target aislado en lab-net |

### 18.3 Diagrama de conectividad

```
HOST (localhost)
     │
     ├── :3000 ─── securescan-frontend ─── securescan-net ─── securescan-api :5000
     ├── :5000 ─── securescan-api ─────────────────────────── securescan-redis :6379
     ├── :8080 ─── securescan-zap ────────────────────────────
     ├── :6379 ─── securescan-redis (solo 127.0.0.1)        │
     ├── :8775 ─── securescan-sqlmapapi (solo 127.0.0.1)    │
     ├── :55553 ── securescan-msfrpcd ────────────────────── │
     │                                                        │
     │                          lab-net ─────────────────────┘
     │                              │
     ├── :3001 ─── juice-shop ──────┤
     ├── :3002 ─── dvwa ────────────┤
     │              └─── dvwa-db ───┤ (sin puerto en host)
     └── :3003 ─── webgoat ─────────┘
```

---

## 19. CONSIDERACIONES DE SEGURIDAD EN EL DESPLIEGUE

### 19.1 Uso exclusivo en red local

SecureScan Pro está diseñado para operar en una red local aislada o en una máquina virtual sin exposición a Internet. Los laboratorios (DVWA, Juice Shop, WebGoat) contienen **vulnerabilidades deliberadas** que pueden ser explotadas por terceros si quedan expuestos.

```bash
# Verificar que los puertos NO están accesibles desde el exterior
# (solo deben responder en localhost)
ss -tlnp | grep -E "3001|3002|3003|8080|55553"
```

### 19.2 Validación de targets en la API

La API implementa validación multi-nivel para prevenir el uso del sistema como herramienta de ataque:

```python
FORBIDDEN_PATTERNS = [
    r'^localhost', r'^127\.', r'^0\.0\.0\.0',
    r'^169\.254\.',          # Link-local
    r'^10\.',                # Clase A privada
    r'^192\.168\.',          # Clase C privada
    r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',  # Clase B privada
    r'^::1', r'^fc00:', r'^fe80:',       # IPv6 privadas
]
```

Los targets del laboratorio (`juice-shop:3000`, `dvwa:80`, `webgoat:8080`) están en la allowlist y siempre pasan la validación.

Para restringir el sistema exclusivamente a los labs del laboratorio:

```bash
# En .env:
RESTRICT_TO_LAB_TARGETS=true
```

### 19.3 Autenticación de la API

Para entornos expuestos a compañeros o evaluadores, habilitar el token de autenticación:

```bash
# Generar token
API_TOKEN=$(openssl rand -hex 32)
echo "API_TOKEN=$API_TOKEN"

# En .env:
API_TOKEN=<token_generado>
NEXT_PUBLIC_API_TOKEN=<mismo_token>

# Reiniciar
docker compose restart api frontend
```

Con el token configurado, todas las peticiones a la API deben incluir el header:
```
X-API-Token: <token>
```

### 19.4 Redis solo en localhost

Redis está mapeado en `127.0.0.1:6379` (no en `0.0.0.0:6379`) para que solo sea accesible desde el host local y no desde otras máquinas en la red local.

### 19.5 Usuarios no-root en los containers

Ambos containers propios usan usuarios no-root:
- `securescan-api`: corre como usuario `scanner` (UID/GID creados en el Dockerfile)
- `securescan-frontend`: corre como usuario `nextjs` (UID 1001)

La única excepción es `cap_net_raw` y `cap_net_admin` agregadas al container API para permitir que nmap funcione correctamente.

### 19.6 Headers de seguridad del frontend

`next.config.mjs` configura los siguientes headers HTTP en todas las respuestas del frontend:

| Header | Valor |
|---|---|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `X-XSS-Protection` | `1; mode=block` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | Desactiva cámara, micrófono, geolocalización |
| `Content-Security-Policy` | CSP completo con fuentes explícitas |

---

*Documento generado a partir del código fuente real de SecureScan Pro v3.0.*  
*Scripts verificados: `start.sh`, `verify.sh`, `fix_frontend_dvwa.sh`, `docker-compose.yml`, `server/Dockerfile`, `Dockerfile.frontend`, `.env.example`.*  
*SENA — Programa Técnico en Seguridad de Aplicaciones Web — Colombia, 2026*
