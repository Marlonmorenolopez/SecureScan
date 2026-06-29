# PRESENTACIÓN DEL PROYECTO DE GRADO
## SecureScan Pro v3.0 — Plataforma Automatizada de Análisis de Seguridad Web

**Aprendiz:** 
**Programa:** Técnico en Seguridad de Aplicaciones Web  
**Institución:** SENA — Servicio Nacional de Aprendizaje (Colombia)  
**Centro de Formación:** [Centro de Formación]  
**Ficha de Caracterización:** [Número de Ficha]  
**Instructor:** [Nombre del Instructor]  
**Fecha de Presentación:** Junio 2026  

---

## TABLA DE CONTENIDOS

1. [Resumen Ejecutivo del Proyecto](#1-resumen-ejecutivo-del-proyecto)
2. [Planteamiento del Problema](#2-planteamiento-del-problema)
3. [Justificación](#3-justificación)
4. [Objetivos](#4-objetivos)
5. [Marco Conceptual y Teórico](#5-marco-conceptual-y-teórico)
6. [Alcance del Proyecto](#6-alcance-del-proyecto)
7. [Descripción Técnica del Sistema](#7-descripción-técnica-del-sistema)
8. [Herramientas de Seguridad Integradas](#8-herramientas-de-seguridad-integradas)
9. [Pipeline de Seguridad — 11 Pasos Secuenciales](#9-pipeline-de-seguridad--11-pasos-secuenciales)
10. [Módulo InjectionScanner — Desarrollo Propio](#10-módulo-injectionscanner--desarrollo-propio)
11. [Sistema de Puntuación de Seguridad](#11-sistema-de-puntuación-de-seguridad)
12. [Laboratorio de Seguridad Integrado](#12-laboratorio-de-seguridad-integrado)
13. [Stack Tecnológico Completo](#13-stack-tecnológico-completo)
14. [Arquitectura del Sistema](#14-arquitectura-del-sistema)
15. [Métricas del Proyecto](#15-métricas-del-proyecto)
16. [Resultados y Demostración](#16-resultados-y-demostración)
17. [Competencias del Programa Demostradas](#17-competencias-del-programa-demostradas)
18. [Consideraciones Éticas y Legales](#18-consideraciones-éticas-y-legales)
19. [Conclusiones](#19-conclusiones)
20. [Glosario de Términos Técnicos](#20-glosario-de-términos-técnicos)
21. [Referencias](#21-referencias)

---

## 1. RESUMEN EJECUTIVO DEL PROYECTO

**SecureScan Pro v3.0** es una plataforma de código abierto para el análisis automatizado de seguridad web, desarrollada como proyecto de grado del programa **Técnico en Seguridad de Aplicaciones Web del SENA**. El sistema integra once herramientas de pentesting reales de la industria —Wappalyzer, Nmap, Patator, Metasploit, ffuf, Gobuster, OWASP ZAP, Nuclei, SQLMap, Searchsploit y un módulo propio InjectionScanner— dentro de un pipeline de ejecución secuencial y automatizado de once pasos.

La plataforma fue concebida para resolver una necesidad real identificada en el contexto formativo: la ausencia de herramientas educativas que integren el ciclo completo de un análisis de seguridad web —desde el reconocimiento inicial hasta la generación de un reporte ejecutivo— en un único sistema accesible para aprendices del área de ciberseguridad.

**Logros técnicos principales del proyecto:**

- Orquestación de 11 herramientas de seguridad real en un pipeline automatizado de 11 pasos secuenciales, donde cada herramienta alimenta a la siguiente con sus resultados.
- Desarrollo del módulo propio `InjectionScanner` (1.689 líneas de Python) que cubre 10 técnicas de inyección activa con 27 subtipos de detección.
- Auto-login automático por laboratorio con manejo de CSRF tokens, JWT y sesiones Spring Security.
- Propagación de cookies de sesión entre herramientas para garantizar coherencia en toda la cadena del análisis.
- Sistema de puntuación de seguridad propio con escala de 13 niveles (A+ a F) y recomendaciones automáticas priorizadas.
- Generación de reportes profesionales en cuatro formatos: HTML, PDF, JSON y CSV.
- Contenedorización completa en Docker Compose con 10 servicios incluyendo tres laboratorios de seguridad vulnerables (DVWA, Juice Shop, WebGoat).
- 23.902 líneas de código total (11.290 Python + ~12.612 TypeScript/TSX).

---

## 2. PLANTEAMIENTO DEL PROBLEMA

### 2.1 Contexto

La ciberseguridad es una de las disciplinas de más rápido crecimiento en el mercado TI colombiano y global. Según el informe ISACA State of Cybersecurity 2024, el 56% de las organizaciones reportan dificultad para encontrar profesionales calificados en seguridad ofensiva y análisis de vulnerabilidades.

En el contexto educativo del programa **Técnico en Seguridad de Aplicaciones Web del SENA**, los aprendices aprenden las herramientas de seguridad de forma aislada y secuencial: primero Nmap, luego OWASP ZAP, luego SQLMap, como asignaturas separadas. Esta fragmentación genera una brecha importante entre el conocimiento teórico de cada herramienta y la comprensión del flujo completo de un análisis de seguridad real, donde las herramientas se encadenan y sus resultados se correlacionan.

### 2.2 Problema central

**¿Cómo integrar las principales herramientas del análisis de seguridad web en un sistema educativo unificado que permita a aprendices del SENA ejecutar un ciclo completo de pentesting de forma automatizada, reproducible y éticamente controlada?**

### 2.3 Problemas específicos identificados

| # | Problema | Impacto |
|---|---|---|
| P1 | Las herramientas de seguridad se usan de forma aislada en el programa formativo | El aprendiz no comprende cómo se encadenan en un análisis real |
| P2 | Configurar y coordinar 10+ herramientas manualmente es complejo para aprendices | Alta barrera de entrada que desmotiva el aprendizaje práctico |
| P3 | Los resultados de múltiples herramientas son difíciles de consolidar y comparar | No hay visión unificada del postura de seguridad de un objetivo |
| P4 | No existen laboratorios locales preconfigurados para practicar de forma legal | Los aprendices practican sobre objetivos reales o no practican |
| P5 | La generación de reportes técnicos de seguridad requiere conocimiento avanzado | Los aprendices no adquieren la habilidad de comunicar hallazgos |

---

## 3. JUSTIFICACIÓN

### 3.1 Relevancia educativa

SecureScan Pro responde directamente a las **Competencias del Técnico en Seguridad de Aplicaciones Web del SENA** definidas en el programa de formación, específicamente:

- **CE01 — Reconocimiento de infraestructura:** Implementado mediante los módulos Wappalyzer y Nmap (Pasos 1 y 2 del pipeline).
- **CE02 — Análisis de vulnerabilidades web:** Implementado mediante ZAP, Nuclei, InjectionScanner y SQLMap (Pasos 7, 8, 9).
- **CE03 — Pruebas de penetración controladas:** Implementado mediante Metasploit en modo auxiliar (Paso 4) y Patator (Paso 3).
- **CE04 — Generación de reportes técnicos:** Implementado mediante `reporter.py` con cuatro formatos de salida.
- **CE05 — Uso de herramientas profesionales:** 11 herramientas de la industria integradas y operativas.

### 3.2 Relevancia técnica

El sistema demuestra dominio de tecnologías que son estándar en la industria de ciberseguridad:

- **Flask** como backend API REST — usado en herramientas profesionales como OWASP WebScarab, ZAP REST API.
- **Next.js 14** como frontend — usado en plataformas SaaS de seguridad como Snyk, Semgrep.
- **Docker Compose** como plataforma de despliegue — estándar en entornos DevSecOps.
- **Redis** como almacenamiento de estado de sesión — usado en plataformas de análisis como Burp Suite Enterprise.

### 3.3 Relevancia práctica

El proyecto no es una demostración teórica: las 11 herramientas integradas son exactamente las mismas que usa un profesional de pentesting en el mundo real. El pipeline implementado sigue la metodología OWASP Testing Guide v4.2 y el marco PTES (Penetration Testing Execution Standard).

### 3.4 Contexto ético y legal

El sistema está diseñado exclusivamente para operar sobre tres laboratorios vulnerables diseñados para el entrenamiento (DVWA, Juice Shop, WebGoat), todos de código abierto y legalmente distribuidos para uso educativo. La API implementa validación de targets que rechaza IPs y dominios reales externos. El uso del sistema fuera de este contexto controlado es responsabilidad exclusiva del operador.

---

## 4. OBJETIVOS

### 4.1 Objetivo General

Desarrollar una plataforma web automatizada de análisis de seguridad que integre once herramientas profesionales de pentesting en un pipeline secuencial de once pasos, con laboratorio de práctica integrado, dashboard de resultados en tiempo real y generación de reportes en múltiples formatos, como proyecto de grado del programa Técnico en Seguridad de Aplicaciones Web del SENA.

### 4.2 Objetivos Específicos

| # | Objetivo | Estado |
|---|---|---|
| OE1 | Integrar Wappalyzer, Nmap, Patator, Metasploit, ffuf, Gobuster, ZAP, Nuclei, SQLMap y Searchsploit en un único sistema orquestado | ✅ Completado |
| OE2 | Desarrollar un módulo propio `InjectionScanner` que cubra 10 técnicas de inyección activa | ✅ Completado |
| OE3 | Implementar auto-login automático para los tres laboratorios con manejo de CSRF, JWT y cookies de sesión | ✅ Completado |
| OE4 | Construir un sistema de puntuación de seguridad (0-100) con escala de calificación (A+ a F) y recomendaciones priorizadas | ✅ Completado |
| OE5 | Desarrollar un dashboard interactivo en Next.js con visualización de resultados en tiempo real (polling) | ✅ Completado |
| OE6 | Implementar generación de reportes en cuatro formatos: HTML, PDF, JSON y CSV | ✅ Completado |
| OE7 | Contenedorizar el sistema completo con Docker Compose incluyendo DVWA, Juice Shop y WebGoat como laboratorio | ✅ Completado |
| OE8 | Implementar mecanismos de resiliencia: Circuit Breaker, retry con backoff exponencial y timeout seguro con threading.Event | ✅ Completado |

---

## 5. MARCO CONCEPTUAL Y TEÓRICO

### 5.1 Seguridad de Aplicaciones Web — OWASP Top 10 2021

El OWASP Top 10 2021 es el estándar internacional de referencia para las vulnerabilidades más críticas en aplicaciones web. SecureScan Pro cubre la detección de las diez categorías:

| Categoría OWASP | Herramienta(s) que la detectan en SecureScan Pro |
|---|---|
| A01 — Broken Access Control | ZAP Active Scan, Nuclei (templates: access-control) |
| A02 — Cryptographic Failures | Nuclei (templates: ssl, jwt), ZAP Spider |
| A03 — Injection | InjectionScanner (10 técnicas), SQLMap, ZAP |
| A04 — Insecure Design | ZAP, Nuclei (templates: misconfig) |
| A05 — Security Misconfiguration | Nuclei (templates: misconfig, header), Nmap scripts NSE |
| A06 — Vulnerable and Outdated Components | Wappalyzer (versiones) + Searchsploit (CVEs) |
| A07 — Identification and Authentication Failures | Patator (brute force), ZAP, Nuclei (templates: default-login) |
| A08 — Software and Data Integrity Failures | Nuclei (templates: token, cors) |
| A09 — Security Logging and Monitoring Failures | ZAP (headers), Nuclei (templates: exposure) |
| A10 — Server-Side Request Forgery | InjectionScanner (SSRF), Nuclei (templates: ssrf) |

### 5.2 Metodología PTES (Penetration Testing Execution Standard)

El pipeline de SecureScan Pro sigue las siete fases del estándar PTES:

| Fase PTES | Paso(s) en SecureScan Pro | Herramienta(s) |
|---|---|---|
| 1. Pre-engagement | Auto-login (previo al pipeline) | `orchestrator._get_session_for_target()` |
| 2. Intelligence Gathering | Pasos 1-2 | Wappalyzer, Nmap |
| 3. Threat Modeling | Paso 4, 10 | Metasploit, Searchsploit |
| 4. Vulnerability Analysis | Pasos 5-9 | ffuf, Gobuster, ZAP, Nuclei, InjectionScanner |
| 5. Exploitation | Pasos 3, 9 | Patator, SQLMap, InjectionScanner |
| 6. Post Exploitation | Paso 11 | Scoring, correlación de exploits |
| 7. Reporting | Endpoint `/api/scan/<id>/report` | `reporter.py` (4 formatos) |

### 5.3 Conceptos técnicos clave

**DAST (Dynamic Application Security Testing):** Técnica de análisis de seguridad que prueba la aplicación en ejecución enviando peticiones reales y observando las respuestas. OWASP ZAP es la herramienta DAST de referencia del proyecto. Se complementa con las técnicas activas del módulo InjectionScanner.

**CVE (Common Vulnerabilities and Exposures):** Sistema de identificación estándar de vulnerabilidades de seguridad conocidas. Searchsploit y Nuclei correlacionan los hallazgos del escaneo con CVEs específicos.

**CVSS (Common Vulnerability Scoring System):** Sistema de puntuación de vulnerabilidades en escala 0-10, donde 10 es la más crítica. El sistema de puntuación de SecureScan Pro se inspira en esta metodología para su escala 0-100.

**Pipeline de seguridad:** Secuencia ordenada de herramientas de análisis donde los resultados de cada etapa alimentan a la siguiente. En SecureScan Pro, la cookie de sesión obtenida por Patator (Paso 3) se propaga a ZAP, Nuclei, InjectionScanner y SQLMap (Pasos 7-9).

**Circuit Breaker:** Patrón de diseño de software que previene llamadas repetidas a un servicio que está fallando. Implementado en dos capas (Flask y orquestador) para gestionar fallos de red en el laboratorio.

**Orquestador:** Componente central que coordina la ejecución de múltiples herramientas, gestiona timeouts, maneja errores y agrega resultados. `server/modules/orchestrator.py` es el corazón del sistema (1.107 líneas).

---

## 6. ALCANCE DEL PROYECTO

### 6.1 Lo que incluye el proyecto

- Sistema completo funcional con backend Flask, frontend Next.js y 11 módulos de seguridad.
- Tres laboratorios vulnerables preconfigurados: DVWA (PHP), Juice Shop (Node.js), WebGoat (Java).
- Auto-login automático para los tres laboratorios con manejo de CSRF, JWT y Spring Security.
- Generación de reportes en HTML, PDF, JSON y CSV.
- Dashboard interactivo con visualización en tiempo real.
- Documentación técnica completa (5 documentos, este siendo uno de ellos).
- Scripts de automatización de despliegue y verificación.
- Sistema de puntuación de seguridad con recomendaciones automáticas.

### 6.2 Lo que no incluye el proyecto (fuera de alcance)

- Análisis de seguridad de redes (WiFi, Bluetooth, protocolos de capa de red).
- Análisis estático de código fuente (SAST).
- Ingeniería social y phishing.
- Análisis de binarios o firmware.
- Escaneo de infraestructura en la nube (AWS, GCP, Azure).
- Soporte para sistemas operativos Windows o macOS en el servidor.
- Acceso multi-usuario simultáneo (diseñado para un único operador a la vez).

### 6.3 Limitaciones conocidas

| Limitación | Causa | Mitigación |
|---|---|---|
| Metasploit puede tardar 5 min en arrancar | JVM de Metasploit Framework | Modo simulación automático si no está listo |
| ZAP consume hasta 3 GB de RAM | JVM de OWASP ZAP | Límite configurado en docker-compose.yml |
| No soporta ARM (Apple Silicon) | Metasploit Framework no tiene imagen arm64 | Soportado solo en x86_64 |
| Los escaneos ZAP + Nuclei tardan ~20 min | Amplitud de las pruebas | Timeouts configurables por variable de entorno |
| Un scan a la vez por instancia | Threading del servidor Flask | Escalable con múltiples instancias si se requiere |

---

## 7. DESCRIPCIÓN TÉCNICA DEL SISTEMA

### 7.1 Componentes principales

SecureScan Pro está estructurado en cuatro capas:

```
┌─────────────────────────────────────────────────────────────┐
│  CAPA 4: PRESENTACIÓN                                        │
│  Next.js 14 / React 18 / TypeScript / Tailwind CSS          │
│  Shadcn/ui + Radix UI + Recharts                            │
└─────────────────────────────┬───────────────────────────────┘
                              │ REST JSON (HTTP :5000)
┌─────────────────────────────▼───────────────────────────────┐
│  CAPA 3: API Y LÓGICA DE NEGOCIO                             │
│  Flask 3.x / Gunicorn / Python 3.11                          │
│  Redis 7 (estado de escaneos) / Flask-Limiter / CORS         │
└─────────────────────────────┬───────────────────────────────┘
                              │ Python calls
┌─────────────────────────────▼───────────────────────────────┐
│  CAPA 2: ORQUESTACIÓN Y MÓDULOS DE SEGURIDAD                 │
│  orchestrator.py — Pipeline secuencial de 11 pasos           │
│  11 módulos: wappalyzer, nmap, patator, metasploit,          │
│  ffuf, gobuster, zap, nuclei, injection_scanner,             │
│  sqlmap, searchsploit                                         │
└─────────────────────────────┬───────────────────────────────┘
                              │ Docker network
┌─────────────────────────────▼───────────────────────────────┐
│  CAPA 1: INFRAESTRUCTURA                                     │
│  Docker Compose — 10 servicios                               │
│  DVWA / Juice Shop / WebGoat (laboratorios)                  │
│  OWASP ZAP / SQLMap API / Metasploit RPC                     │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Flujo de una sesión de escaneo

```
Usuario en http://localhost:3000
    │
    │ 1. Selecciona target (ej: Juice Shop)
    │    Activa herramientas (checkboxes)
    │    Hace clic en "Iniciar Escaneo"
    │
    ▼
POST /api/scan
    │ Validación de target y UUID
    │ Guarda estado inicial en Redis
    │ Lanza thread de escaneo (daemon=False)
    │ Responde: { "jobId": "uuid-v4", "status": "running" }
    │
    ├──→ Frontend inicia polling GET /api/scan/<id>/status cada 2s
    │    └── scan-progress.tsx muestra paso activo + barra de progreso
    │
    └──→ Thread de escaneo ejecuta el pipeline secuencial
         │
         ├── Auto-login → obtiene session_cookie
         ├── Paso 1: Wappalyzer → technologies[]
         ├── Paso 2: Nmap → ports[]
         ├── Paso 3: Patator → brute_force_results[]
         ├── Paso 4: Metasploit → metasploit[]
         ├── Paso 5: ffuf → ffuf_endpoints[]
         ├── Paso 6: Gobuster → directories[]
         ├── Paso 7: ZAP → vulnerabilities[]
         ├── Paso 8: Nuclei → nuclei_findings[]
         ├── Paso 9: InjectionScanner → sqli_results[]
         ├── Paso 10: Searchsploit → exploits[]
         └── Paso 11: Scoring → score { total, grade, riskLevel }
              │
              └── Redis: status = "completed"
                    │
                    └── Frontend: muestra results-dashboard.tsx
                          │
                          └── Usuario descarga reporte (HTML/PDF/JSON/CSV)
```

---

## 8. HERRAMIENTAS DE SEGURIDAD INTEGRADAS

### 8.1 Wappalyzer — Paso 1: Reconocimiento Tecnológico

**Categoría:** OSINT / Fingerprinting  
**Implementación:** Librería Python `python-Wappalyzer` + fallback a CLI y simulación  
**Archivo:** `server/modules/wappalyzer.py` (228 líneas)

Wappalyzer analiza las cabeceras HTTP, cookies, scripts y metadatos HTML de la aplicación objetivo para identificar el stack tecnológico completo: CMS, frameworks frontend y backend, servidores web, librerías JavaScript y plataformas.

**Por qué es el primer paso:** El perfil tecnológico determina qué módulos Nuclei aplicar, qué exploits buscar en Searchsploit y qué módulos de Metasploit son relevantes. Sin esta información, los pasos posteriores serían genéricos e ineficientes.

**Ejemplo de salida:**
```json
[
  { "name": "Node.js",  "version": "18.x", "category": "javascript-frameworks" },
  { "name": "Express",  "version": "4.x",  "category": "web-frameworks" },
  { "name": "Angular",  "version": "14.x", "category": "javascript-frameworks" }
]
```

### 8.2 Nmap — Paso 2: Escaneo de Infraestructura

**Categoría:** Network Discovery / Port Scanning  
**Implementación:** Subproceso con salida XML parseada  
**Archivo:** `server/modules/nmap_scanner.py` (359 líneas)  
**Versión:** Nmap 7.93+ instalado en el Dockerfile (APT)

Nmap descubre los puertos TCP abiertos del objetivo, identifica los servicios activos en cada puerto, detecta versiones de software y ejecuta scripts NSE para obtener información adicional como banners, certificados SSL y configuraciones expuestas.

**Comando ejecutado:**
```bash
nmap -sV -sC -O --script=banner,version -T4 -p <puertos> --open -oX - <hostname>
```

**Por qué es el segundo paso:** Los puertos y versiones de servicios detectadas se usan en el Paso 10 (Searchsploit) para buscar CVEs específicos a las versiones encontradas.

### 8.3 Patator — Paso 3: Pruebas de Autenticación

**Categoría:** Brute Force / Credential Stuffing  
**Implementación:** Librería Python `requests` con cascada a binario `patator`  
**Archivo:** `server/modules/patator.py` (666 líneas)  

Patator prueba combinaciones de credenciales contra los formularios de login de la aplicación objetivo. Maneja automáticamente tokens CSRF (DVWA y WebGoat) y autenticación JSON con JWT (Juice Shop).

**Por qué es el tercer paso:** La cookie de sesión obtenida si Patator encuentra credenciales válidas se propaga a todos los pasos posteriores (4-10), garantizando que ZAP, Nuclei e InjectionScanner tengan acceso autenticado a las funcionalidades protegidas del sistema.

**Wordlists integradas:**
```
Usuarios: admin, guest, admin@juice-sh.op, securescan, jsmith, ...
Contraseñas: password, admin123, Password, demo1234, 123456, ...
```

### 8.4 Metasploit Framework — Paso 4: Validación de Exploits

**Categoría:** Exploitation Framework  
**Implementación:** `pymetasploit3` vía Console RPC (`msfrpcd:55553`)  
**Archivo:** `server/modules/metasploit.py` (288 líneas)  
**Imagen Docker:** `metasploitframework/metasploit-framework:latest`

Metasploit ejecuta únicamente **módulos auxiliares de verificación** —no exploits destructivos— para confirmar si las vulnerabilidades detectadas son realmente explotables en el objetivo. En modo educativo, esto demuestra cómo se validaría un hallazgo en un pentest real.

**Módulos base siempre ejecutados:**
```
auxiliary/scanner/http/http_version   — fingerprinting versión HTTP
auxiliary/scanner/http/options        — métodos HTTP permitidos
auxiliary/scanner/http/dir_listing    — listado de directorios
auxiliary/scanner/http/robots_txt     — análisis de robots.txt
```

**Módulos adicionales** se seleccionan automáticamente según las tecnologías detectadas por Wappalyzer (Apache Tomcat → tomcat_mgr_login, WordPress → wp_login, etc.).

### 8.5 ffuf — Paso 5: Fuzzing de Endpoints

**Categoría:** Web Content Discovery / Fuzzing  
**Implementación:** Subproceso Go binary, salida JSON  
**Archivo:** `server/modules/ffuf.py` (305 líneas)  
**Versión:** ffuf v2.1.0 (instalado con `go install` en el Dockerfile)

ffuf (Fuzz Faster U Fool) descubre rutas y archivos ocultos en el servidor web mediante fuzzing de alta velocidad. Usa la wordlist de SecLists con filtrado por códigos de estado HTTP relevantes.

**Comando ejecutado:**
```bash
ffuf -u <target>/FUZZ -w /opt/SecLists/Discovery/Web-Content/common.txt
     -o results.json -of json -H "Cookie: <session_cookie>"
     -mc 200,204,301,302,307,401,403 -ac -t 10 -timeout 10
```

### 8.6 Gobuster — Paso 6: Enumeración de Directorios

**Categoría:** Directory/File Enumeration  
**Implementación:** Subproceso Go binary  
**Archivo:** `server/modules/gobuster.py` (769 líneas)  
**Versión:** gobuster v3.6.0 (instalado con `go install` en el Dockerfile)

Gobuster realiza una enumeración más profunda de directorios y archivos que ffuf, seleccionando la wordlist más adecuada según el fingerprint tecnológico del objetivo. Para WebGoat, enumera bajo el path `/WebGoat/` en lugar de la raíz `/`.

### 8.7 OWASP ZAP — Paso 7: DAST Completo

**Categoría:** Dynamic Application Security Testing  
**Implementación:** REST API de ZAP (`http://zap:8080`)  
**Archivo:** `server/modules/zap_scanner.py` (1.102 líneas)  
**Imagen Docker:** `ghcr.io/zaproxy/zaproxy:stable` con 3 GB de límite de RAM

OWASP ZAP es el escáner DAST de referencia de OWASP, usado por profesionales de seguridad a nivel mundial. En SecureScan Pro ejecuta la función unificada `run_zap_full()` que combina:

1. **Spider:** Rastrea todas las páginas y endpoints de la aplicación.
2. **URL Injection:** Inyecta las URLs descubiertas por ffuf y Gobuster en ZAP para ampliar la cobertura.
3. **Active Scan:** Prueba cada parámetro encontrado en busca de más de 40 tipos de vulnerabilidades.

La política de escaneo se selecciona automáticamente según el laboratorio detectado: `Dev CICD` para Juice Shop, `Dev Standard` para DVWA y WebGoat.

### 8.8 Nuclei — Paso 8: Escaneo por Plantillas

**Categoría:** Template-based Vulnerability Scanner  
**Implementación:** Subproceso Go binary con salida JSONL  
**Archivo:** `server/modules/nuclei.py` (560 líneas)  
**Versión:** nuclei v3.2.4 (instalado con `go install` en el Dockerfile)

Nuclei ejecuta un amplio conjunto de plantillas YAML de vulnerabilidades conocidas. La librería pública de plantillas contiene más de 12.841 templates; SecureScan Pro filtra a ~5.000 usando los tags relevantes para el objetivo y excluyendo protocolos no web (`-ept dns,ssl,tcp,whois,javascript`).

**Tags por laboratorio:**

| Laboratorio | Tags aplicados |
|---|---|
| Juice Shop | `cve,sqli,xss,jwt,cors,ssrf,owasp,exposure,swagger,token,oauth,misconfig,header,redirect,api,nodejs` |
| DVWA | `cve,sqli,xss,lfi,rce,rfi,default-login,misconfig,header,php,exposure` |
| WebGoat | `cve,sqli,xss,jwt,xxe,ssrf,cors,misconfig,header,java,spring,exposure` |
| Genérico | `cve,exposure,misconfig,default-login,header,cors,ssrf,token,redirect` |

### 8.9 InjectionScanner (Módulo Propio) — Paso 9

**Categoría:** Active Injection Testing  
**Implementación:** Módulo Python desarrollado 100% para SecureScan Pro  
**Archivo:** `server/modules/injection_scanner.py` (1.689 líneas — el más extenso del proyecto)

Desarrollado específicamente como contribución original del proyecto, el `InjectionScanner` cubre 10 técnicas de inyección activa con 27 subtipos. Ver sección 10 para descripción detallada.

**Fallback:** Si el módulo no está disponible, el sistema cae automáticamente en SQLMap (`sqlmapapi`) para cubrir al menos la inyección SQL.

### 8.10 Searchsploit — Paso 10: Correlación de Exploits

**Categoría:** Exploit Database Search  
**Implementación:** Subproceso CLI + flag `--json`, búsqueda local offline  
**Archivo:** `server/modules/searchsploit.py` (262 líneas)  
**Instalación:** ExploitDB clonado en `/opt/exploitdb` durante el build del Dockerfile

Searchsploit busca en la base de datos local de ExploitDB exploits públicos que correspondan a las tecnologías y versiones detectadas por Wappalyzer (Paso 1) y Nmap (Paso 2). La búsqueda es **offline** (no requiere conexión a Internet durante el escaneo), usando el repositorio clonado en el momento del build.

**Correlación automática:** El orquestador cruza los exploits encontrados con las vulnerabilidades del Paso 7 (ZAP) y del Paso 9 (InjectionScanner). Los hallazgos correlacionados reciben una penalización adicional de 8 puntos en la puntuación de seguridad.

---

## 9. PIPELINE DE SEGURIDAD — 11 PASOS SECUENCIALES

El pipeline es la característica técnica central de SecureScan Pro. Cada paso tiene un propósito específico y sus resultados alimentan a los pasos siguientes.

```
INICIO: POST /api/scan { "target": "http://juice-shop:3000" }
│
├─ Auto-login ──────────────────── _get_session_for_target()
│   └─ session_cookie disponible para Pasos 3-10
│
│   RESULTADOS
│   PARCIALES  ──── Cada paso guarda en Redis inmediatamente
│   EN REDIS        (visible en el polling del frontend)
│
Paso 1:  Wappalyzer  ──────────── Perfil tecnológico
          └─→ technologies[] orienta tags Nuclei (Paso 8) y exploits (Paso 10)
│
Paso 2:  Nmap  ─────────────────── Puertos y servicios
          └─→ ports[] orienta módulos Metasploit (Paso 4) y exploits (Paso 10)
│
Paso 3:  Patator  ──────────────── Fuerza bruta de credenciales
          └─→ brute_force_results[] + session_cookie (si encuentra creds)
│
Paso 4:  Metasploit  ───────────── Módulos auxiliares de verificación
          └─→ metasploit[] (usa technologies[] del Paso 1)
│
Paso 5:  ffuf  ─────────────────── Fuzzing de endpoints HTTP
          └─→ ffuf_endpoints[] (usa session_cookie del Paso 3)
│
Paso 6:  Gobuster  ─────────────── Enumeración de directorios
          └─→ directories[] (usa session_cookie del Paso 3)
│
Paso 7:  OWASP ZAP Full Scan  ──── Spider + Active Scan DAST
          ├─→ Inyecta URLs de Paso 5 y Paso 6 antes del Active Scan
          └─→ vulnerabilities[] + spider_results[]
│
Paso 8:  Nuclei  ───────────────── Escaneo por plantillas YAML
          ├─→ Usa technologies[] del Paso 1 para seleccionar tags
          └─→ nuclei_findings[]
│
Paso 9:  InjectionScanner  ─────── 10 técnicas de inyección activa
          └─→ sqli_results[] (usa session_cookie del Paso 3)
│
Paso 10: Searchsploit  ─────────── Correlación con ExploitDB offline
          ├─→ Usa technologies[] del Paso 1 y ports[] del Paso 2
          └─→ exploits[] con correlación a vulnerabilidades de ZAP
│
Paso 11: Scoring  ──────────────── Puntuación global (0-100)
          ├─→ Agrega: vulnerabilities + exploits + brute_force + nuclei
          └─→ score { total, grade, riskLevel, recommendations }
│
FIN: status = "completed"
     Frontend muestra ResultsDashboard con todos los resultados
     Usuario puede descargar reporte en HTML, PDF, JSON o CSV
```

### 9.1 Propagación de cookies entre herramientas

Uno de los logros técnicos más relevantes del pipeline es la propagación coherente de la cookie de sesión. Sin esto, cada herramienta analizaría la aplicación como usuario anónimo, perdiendo acceso a todas las funcionalidades autenticadas.

```
Auto-login (previo al pipeline)
    │
    └── session_cookie = "PHPSESSID=abc123; security=low"
            │
            ├── Paso 3: Patator usa session_cookie
            │     └── Si encuentra creds válidas, actualiza session_cookie
            │
            ├── Paso 5: ffuf -H "Cookie: <session_cookie>"
            ├── Paso 6: Gobuster con cabecera Cookie
            ├── Paso 7: ZAP configurado con session_cookie
            ├── Paso 8: Nuclei -H "Cookie: <session_cookie>"
            └── Paso 9: InjectionScanner usa session_cookie
```

---

## 10. MÓDULO INJECTIONSCANNER — DESARROLLO PROPIO

### 10.1 Contexto de su desarrollo

El módulo `InjectionScanner` es la contribución técnica más original del proyecto. Fue desarrollado completamente para SecureScan Pro porque ninguna herramienta existente cubría las 10 técnicas de inyección de forma integrada, con soporte específico para los tres laboratorios del sistema y compatible con la API interna del orquestador.

**Tamaño:** 1.689 líneas de Python — el módulo más extenso del backend.

### 10.2 Técnicas de inyección cubiertas

| # | Técnica | Subtipos detectados |
|---|---|---|
| 1 | **SQL Injection** | Error-based, UNION-based, Boolean-Blind, Time-based Blind, Auth Bypass, Stacked Queries, Second-Order |
| 2 | **NoSQL Injection** | MongoDB operators (`$gt`, `$ne`), regex bypass (`$regex`) |
| 3 | **XPath Injection** | Auth bypass (`' or '1'='1`), error-based extraction |
| 4 | **XML / XXE** | File read (`/etc/passwd`), OOB (Out-Of-Band), Blind XXE |
| 5 | **XSS** | Reflected, Stored, DOM-based |
| 6 | **Command Injection** | Semicolon (`;`), pipe (`|`), backtick (`` ` ``), AND (`&&`) |
| 7 | **Path Traversal** | LFI (`../../../etc/passwd`), Windows paths (`..\\..\\Windows\\System32`) |
| 8 | **SSRF** | Acceso a hosts internos, bypass CORS, redirección abierta |
| 9 | **SSTI** | Jinja2 (`{{7*7}}`), Twig, Freemarker, Velocity, Pebble |
| 10 | **LDAP Injection** | Filter bypass (`*)(uid=*))(|(uid=*`), wildcard injection |

### 10.3 Arquitectura del módulo

```python
class InjectionType(str, Enum):
    SQL_ERROR       = "sql_error_based"
    SQL_UNION       = "sql_union_based"
    SQL_BOOLEAN     = "sql_boolean_blind"
    SQL_TIME        = "sql_time_based"
    SQL_AUTH_BYPASS = "sql_auth_bypass"
    SQL_STACKED     = "sql_stacked_queries"
    SQL_SECOND_ORDER = "sql_second_order"
    NOSQL           = "nosql_injection"
    XPATH           = "xpath_injection"
    XXE             = "xxe"
    XSS_REFLECTED   = "xss_reflected"
    XSS_STORED      = "xss_stored"
    XSS_DOM         = "xss_dom"
    COMMAND         = "command_injection"
    PATH_TRAVERSAL  = "path_traversal"
    SSRF            = "ssrf"
    SSTI            = "ssti"
    LDAP            = "ldap_injection"

@dataclass
class InjectionFinding:
    type: InjectionType
    url: str
    parameter: str
    payload: str
    evidence: str
    severity: str
    description: str
    cwe: str          # Identificador CWE de la vulnerabilidad
    tool: str = "injection_scanner"
```

### 10.4 Compatibilidad por laboratorio

| Laboratorio | Protocolo | Auth | Endpoints objetivo |
|---|---|---|---|
| Juice Shop | REST JSON | JWT Bearer | `/api/Products/search`, `/rest/products`, `/api/Users` |
| DVWA | Formularios HTML | Cookie (`security=low`) | `/vulnerabilities/sqli/`, `/vulnerabilities/xss_r/` |
| WebGoat | Spring REST JSON | JSESSIONID | `/WebGoat/SqlInjection/`, `/WebGoat/SSRF/`, `/WebGoat/PathTraversal/` |
| Genérico | HTTP estándar | Cookie genérica | Formularios HTML detectados automáticamente |

---

## 11. SISTEMA DE PUNTUACIÓN DE SEGURIDAD

### 11.1 Metodología

El sistema de puntuación (`server/utils/scoring.py`, 530 líneas) calcula una puntuación global de 0 a 100 inspirada en la metodología CVSS, pero adaptada al contexto de un análisis de aplicaciones web.

**Algoritmo base:**
```
Puntuación inicial: 100

Por cada vulnerabilidad:
  - Crítica:  -20 puntos
  - Alta:     -10 puntos
  - Media:     -5 puntos
  - Baja:      -2 puntos
  - Info:      -0.5 puntos

Si existe exploit para una vulnerabilidad: -8 puntos adicionales
Exploit sin vulnerabilidad correlacionada: -3 puntos
Credenciales válidas por brute force:      -10 puntos (alta)

Downgrade automático por hallazgos críticos:
  ≥3 vulnerabilidades críticas → Grade F directo
  ≥1 vulnerabilidad crítica    → Grade D mínimo
  ≥5 vulnerabilidades altas    → Grade C mínimo

Resultado final: max(0, puntuación)
```

### 11.2 Escala de calificación

| Score | Grade | Risk Level | Descripción |
|---|---|---|---|
| 95-100 | **A+** | MINIMAL | Excelente postura de seguridad |
| 90-94 | **A** | MINIMAL | Muy bien — solo issues menores |
| 85-89 | **A-** | LOW | Bien — pocos hallazgos de bajo riesgo |
| 80-84 | **B+** | LOW | Sobre el promedio — algunas áreas a revisar |
| 75-79 | **B** | LOW | Promedio — issues moderados presentes |
| 70-74 | **B-** | MEDIUM | Bajo el promedio — varios issues a resolver |
| 65-69 | **C+** | MEDIUM | Aceptable — mejoras de seguridad necesarias |
| 60-64 | **C** | MEDIUM | Débil — vulnerabilidades significativas |
| 55-59 | **C-** | MEDIUM | Muy débil — brechas de seguridad mayores |
| 50-54 | **D+** | HIGH | Deficiente — correcciones críticas requeridas |
| 45-49 | **D** | HIGH | Muy deficiente — acción inmediata requerida |
| 0-44 | **F** | CRITICAL | Sistema altamente vulnerable |

### 11.3 Recomendaciones automáticas

Además de la puntuación, el sistema genera recomendaciones priorizadas automáticamente según los hallazgos:

```
🚨 URGENT: X critical vulnerabilities detected — immediate remediation required
⚠ HIGH: 8 high severity issues — schedule remediation within 30 days
🔑 CRITICAL: Weak credentials found — admin:password — Change immediately
🛡 HIGH: Known exploits available for detected technologies — Patch immediately
📋 MEDIUM: 15 medium severity issues — address within 90 days
```

---

## 12. LABORATORIO DE SEGURIDAD INTEGRADO

El sistema incluye tres aplicaciones vulnerables preconfiguradas, accesibles localmente sin necesidad de Internet. Todas son proyectos de código abierto diseñados específicamente para entrenamiento en seguridad.

### 12.1 OWASP Juice Shop v17.0.0

**Puerto:** `http://localhost:3001`  
**Stack:** Node.js / Angular / SQLite  
**Imagen:** `bkimminich/juice-shop:v17.0.0`

La aplicación de seguridad más moderna y completa del ecosistema OWASP. Simula una tienda en línea con más de 100 desafíos de seguridad deliberadamente introducidos, cubriendo las 10 categorías del OWASP Top 10 2021.

**Vulnerabilidades que SecureScan Pro detecta en Juice Shop:**

| Categoría | Herramienta | Ejemplo de hallazgo |
|---|---|---|
| SQLi en búsqueda de productos | InjectionScanner / ZAP | `GET /api/Products/search?q=test'` |
| JWT sin verificación de firma | Nuclei (template: jwt) | Token con alg=none |
| XSS en campo de búsqueda | ZAP Active Scan | `<img src=x onerror=alert(1)>` |
| Credenciales débiles | Patator | `admin@juice-sh.op / admin123` |
| CORS misconfiguration | Nuclei (template: cors) | Wildcard origin permitido |
| Endpoint API sin autenticación | ZAP Spider + ffuf | `/api/Users` accesible sin token |

### 12.2 DVWA (Damn Vulnerable Web Application)

**Puerto:** `http://localhost:3002`  
**Stack:** PHP / Apache / MariaDB 10.11  
**Imagen:** `ghcr.io/digininja/dvwa:latest`

La aplicación de seguridad PHP más utilizada en el mundo para entrenamiento. Categoriza sus vulnerabilidades por nivel de dificultad (low/medium/high/impossible). SecureScan Pro fuerza el nivel a `low` mediante auto-login para maximizar la detección.

**Corrección técnica relevante (logro del proyecto):** DVWA requiere un token CSRF específico de `security.php` para aceptar el cambio de nivel de seguridad. Sin este token, DVWA mantiene el nivel `impossible` silenciosamente y SQLMap y Nuclei no pueden detectar las vulnerabilidades. La implementación del auto-login de DVWA resuelve este problema con tres peticiones secuenciales.

**Módulos vulnerables escaneados:**

| Módulo DVWA | Tipo de vulnerabilidad | Herramienta |
|---|---|---|
| `/vulnerabilities/sqli/` | SQL Injection (param: `id`) | SQLMap, InjectionScanner |
| `/vulnerabilities/sqli_blind/` | SQLi Ciega | SQLMap |
| `/vulnerabilities/xss_r/` | XSS Reflejado | ZAP, InjectionScanner |
| `/vulnerabilities/xss_s/` | XSS Almacenado | ZAP |
| `/vulnerabilities/brute/` | Login sin protección | Patator |
| `/vulnerabilities/upload/` | File Upload sin validación | ZAP, Nuclei |

### 12.3 WebGoat

**Puerto:** `http://localhost:3003/WebGoat/`  
**Stack:** Java Spring Boot  
**Imagen:** `webgoat/webgoat:latest`

Aplicación Java OWASP diseñada como plataforma de aprendizaje interactivo. Toda la aplicación está bajo el path `/WebGoat/`, lo que requiere configuración específica en Gobuster y ffuf.

**Corrección técnica relevante:** El nombre de usuario del auto-login tenía un typo (`securesacan` en lugar de `securescan`), lo que hacía que el login siempre fallara para WebGoat. Esta corrección es uno de los 20 fixes documentados en el historial de desarrollo.

---

## 13. STACK TECNOLÓGICO COMPLETO

### 13.1 Backend

| Tecnología | Versión | Rol en el proyecto |
|---|---|---|
| Python | 3.11 | Lenguaje del backend y todos los módulos de seguridad |
| Flask | 3.x | Framework web API REST |
| Gunicorn | 21.2+ | Servidor WSGI de producción (2 workers, 4 threads) |
| Redis | 7 | Almacenamiento de estado de escaneos con TTL |
| Flask-CORS | 4.x | Middleware de CORS configurable por variable de entorno |
| Flask-Limiter | 3.5+ | Rate limiting (20 req/h en POST /api/scan) |
| pdfkit | 1.x | Generación de PDF (wrapper de wkhtmltopdf) |
| python-Wappalyzer | 0.3+ | Fingerprinting tecnológico |
| pymetasploit3 | 1.0+ | Cliente RPC de Metasploit Framework |
| BeautifulSoup4 | 4.12+ | Parser HTML para auto-login y Wappalyzer |
| docker (SDK) | 7.1+ | Control de containers Docker (endpoints /api/lab/) |

### 13.2 Herramientas de seguridad instaladas en el container

| Herramienta | Versión | Instalación | Lenguaje |
|---|---|---|---|
| Nmap | 7.93+ | APT | C |
| Patator | APT | APT | Python |
| SQLMap | git HEAD | Git clone | Python |
| Gobuster | v3.6.0 | `go install` | Go |
| ffuf | v2.1.0 | `go install` | Go |
| Nuclei | v3.2.4 | `go install` | Go |
| Searchsploit | git HEAD | Git clone (ExploitDB) | Bash |
| wkhtmltopdf | 0.12.6+ | APT | C++ |
| Go runtime | 1.22.5 | Instalación manual | — |

### 13.3 Frontend

| Tecnología | Versión | Rol |
|---|---|---|
| Next.js | 14.2.5 | Framework React con App Router |
| React | 18.3.1 | Librería de interfaz de usuario |
| TypeScript | 5.4.x | Tipado estático estricto |
| Tailwind CSS | 3.4.x | Framework de estilos utility-first |
| Shadcn/ui | — | Componentes accesibles sobre Radix UI (55 archivos) |
| Radix UI | múltiple | Primitivos de UI accesibles |
| TanStack Query | 5.28.x | Data fetching y cache |
| Recharts | 2.12.x | Gráficos y visualizaciones de resultados |
| Lucide React | 0.400.x | Iconos SVG |
| pnpm | 8.15.0 | Package manager |
| Node.js | 20 LTS | Runtime del servidor Next.js |

### 13.4 Infraestructura

| Componente | Tecnología | Versión |
|---|---|---|
| Orquestación de containers | Docker Compose v2 | plugin v2.x |
| Imagen base backend | python:3.11-slim-bookworm | Debian 12 |
| Imagen base frontend | node:20-alpine | Alpine Linux |
| Laboratorio 1 | bkimminich/juice-shop | v17.0.0 |
| Laboratorio 2 | ghcr.io/digininja/dvwa | latest |
| Base de datos DVWA | mariadb | 10.11 |
| Laboratorio 3 | webgoat/webgoat | latest |
| DAST Engine | ghcr.io/zaproxy/zaproxy | stable |
| Exploitation | metasploitframework/metasploit-framework | latest |
| Cache / Estado | redis | 7-alpine |

---

## 14. ARQUITECTURA DEL SISTEMA

### 14.1 Diagrama de componentes

```
┌──────────────────────────────────────────────────────────────────┐
│                    NAVEGADOR DEL USUARIO                          │
│                     http://localhost:3000                         │
└──────────────────────────┬───────────────────────────────────────┘
                           │ HTTP REST JSON
┌──────────────────────────▼───────────────────────────────────────┐
│              FRONTEND — Next.js 14 / React 18                     │
│  ┌───────────────┐ ┌─────────────────┐ ┌──────────────────────┐  │
│  │  scan-form    │ │  scan-progress  │ │  results-dashboard   │  │
│  │  .tsx         │ │  .tsx           │ │  .tsx (1249 líneas)  │  │
│  │  (440 líneas) │ │  (313 líneas)   │ │                      │  │
│  └───────────────┘ └─────────────────┘ └──────────────────────┘  │
│  lib/api-client.ts (491 líneas) — lib/scan-context.tsx (350)     │
└──────────────────────────┬───────────────────────────────────────┘
                           │ :5000
┌──────────────────────────▼───────────────────────────────────────┐
│              BACKEND — Flask / Gunicorn / Python 3.11             │
│                      server/app.py (1010 líneas)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Auth Token   │  │ Rate Limiter │  │  Circuit Breaker     │   │
│  │ X-API-Token  │  │ 20/hora POST │  │  (doble capa)        │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │           SecurityOrchestrator                           │    │
│  │         orchestrator.py (1107 líneas)                    │    │
│  │                                                          │    │
│  │  P1:Wappalyzer P2:Nmap  P3:Patator P4:Metasploit        │    │
│  │  P5:ffuf  P6:Gobuster P7:ZAP  P8:Nuclei                 │    │
│  │  P9:InjectionScanner P10:Searchsploit P11:Scoring        │    │
│  └──────────────────────────────────────────────────────────┘    │
└────┬──────────────┬──────────────────────┬────────────────────────┘
     │              │                      │
┌────▼────┐  ┌──────▼──────┐    ┌─────────▼──────────────────────┐
│ Redis 7 │  │  ZAP :8080  │    │        lab-net                  │
│ :6379   │  │  (3 GB RAM) │    │  juice-shop:3000 / dvwa:80     │
│ Estado  │  │  DAST       │    │  webgoat:8080                  │
│ Scans   │  └─────────────┘    │  sqlmapapi:8775                │
└─────────┘                     │  msfrpcd:55553                 │
                                └─────────────────────────────────┘
```

### 14.2 Patrón de resiliencia — Circuit Breaker

```
Petición de escaneo entrante
        │
        ▼
[¿Circuito abierto para este target?]
        │
   Sí ─→ 429 Too Many Requests (sin lanzar el scan)
        │
   No ─→ [Lanzar thread de escaneo]
              │
        [¿Herramienta falla?]
              │
         Sí ─→ _cb_record_failure(target)
              │ ¿failure_threshold alcanzado?
              │   Sí → Estado OPEN (bloqueado 60s)
              │
         No ─→ _cb_record_success(target)
                 Estado CLOSED (normal)
```

---

## 15. MÉTRICAS DEL PROYECTO

### 15.1 Líneas de código por componente

| Componente | Archivos | Líneas |
|---|---|---|
| Backend Python (módulos de seguridad) | 13 archivos | 8.734 líneas |
| Backend Python (API Flask) | 1 archivo | 1.010 líneas |
| Backend Python (utils) | 2 archivos | 1.666 líneas |
| **Total Backend Python** | **16 archivos** | **11.290 líneas** |
| Frontend TypeScript (páginas + componentes) | 16 archivos | 5.831 líneas |
| Frontend TypeScript (componentes Shadcn/ui) | 55 archivos | 6.281 líneas |
| **Total Frontend TypeScript** | **71 archivos** | **12.112 líneas** |
| **TOTAL DEL PROYECTO** | **~100 archivos** | **~23.902 líneas** |

### 15.2 Herramientas y servicios integrados

| Categoría | Cantidad |
|---|---|
| Herramientas de seguridad integradas | 11 |
| Servicios Docker en el docker-compose | 10 |
| Laboratorios vulnerables incluidos | 3 |
| Técnicas de inyección en InjectionScanner | 10 |
| Subtipos de inyección | 27 |
| Formatos de reporte soportados | 4 (HTML, PDF, JSON, CSV) |
| Niveles de grade de seguridad | 13 (A+ a F) |
| Pasos del pipeline secuencial | 11 |
| Correcciones técnicas documentadas | 35+ |
| Endpoints de la API REST | 11 |

### 15.3 Tiempo de desarrollo

| Fase | Descripción |
|---|---|
| Investigación y diseño | Selección de herramientas, diseño de arquitectura |
| Desarrollo del backend | Flask API, todos los módulos de seguridad, orquestador |
| Desarrollo del frontend | Next.js, todos los componentes, API client, Context |
| Integración y debugging | Corrección de 35+ bugs, ajuste del pipeline |
| Documentación | 5 documentos técnicos completos |
| Testing en laboratorio | Verificación end-to-end en los 3 labs |

---

## 16. RESULTADOS Y DEMOSTRACIÓN

### 16.1 Resultado de escaneo típico sobre DVWA

**Target:** `http://dvwa:80` (Nivel de seguridad: Low)  
**Herramientas activas:** Todas (11 pasos)  
**Duración típica del escaneo:** 25-35 minutos

**Resultados esperados:**

| Herramienta | Hallazgos típicos |
|---|---|
| Wappalyzer | PHP 8.x, Apache 2.4.x, MariaDB 10.11, jQuery 3.x |
| Nmap | Puerto 80 abierto (Apache), banner HTTP, posible OS detection |
| Patator | Credencial válida: `admin` / `password` |
| Metasploit | `apache tomcat` — módulos auxiliares sin resultado en DVWA PHP |
| ffuf | 40-60 endpoints descubiertos (login.php, setup.php, dvwa/) |
| Gobuster | Directorios: /vulnerabilities/, /includes/, /dvwa/ |
| ZAP | 15-25 alertas: SQLi, XSS Reflejado, XSS Almacenado, CSRF, Cabeceras faltantes |
| Nuclei | 5-10 hallazgos: default-login, PHP version exposed, misconfig headers |
| InjectionScanner | SQLi en `/vulnerabilities/sqli/?id=`, XSS en `/vulnerabilities/xss_r/?name=` |
| Searchsploit | 3-5 exploits para PHP y Apache versiones detectadas |
| **Scoring** | **~40-55/100 — Grade D/D+ — Risk CRITICAL/HIGH** |

### 16.2 Interfaz gráfica — Componentes del dashboard

El dashboard de resultados `results-dashboard.tsx` (1.249 líneas) presenta los hallazgos en 10 tabs:

| Tab | Contenido |
|---|---|
| Resumen | Puntuación visual, grade (ej: D+), gráfico de distribución por severidad |
| Vulnerabilidades | Tabla filtreable con nombre, severidad, URL, descripción y solución |
| Tecnologías | Lista de tecnologías detectadas por Wappalyzer con versiones y categorías |
| Puertos | Tabla de puertos abiertos: puerto, protocolo, servicio, versión |
| Directorios | URLs descubiertas por Gobuster y ffuf con código HTTP |
| SQLi | Resultados del InjectionScanner con técnica, payload y evidencia |
| Nuclei | Hallazgos por template con severidad y referencia CVE |
| Brute Force | Credenciales encontradas por Patator |
| Exploits | Exploits de Searchsploit correlacionados con vulnerabilidades |
| Metasploit | Resultados de módulos auxiliares |

### 16.3 Ejemplo de reporte HTML generado

El reporte HTML incluye:
- Metadata del scan: ID, target, fecha, duración.
- Panel visual de puntuación con grade y risk level.
- Recomendaciones priorizadas (URGENT / HIGH / MEDIUM).
- Tabla de vulnerabilidades con descripción y solución de cada una.
- Tecnologías detectadas, puertos abiertos, directorios descubiertos.
- Exploits correlacionados con sus referencias CVE.
- Todos los contenidos sanitizados con `html.escape()` para prevenir XSS en el propio reporte.

---

## 17. COMPETENCIAS DEL PROGRAMA DEMOSTRADAS

### 17.1 Mapa de competencias SENA — Técnico en Seguridad de Aplicaciones Web

| Competencia del Programa | Evidencia en SecureScan Pro |
|---|---|
| Identificar vulnerabilidades en aplicaciones web | Pipeline completo: ZAP, Nuclei, InjectionScanner (10 técnicas), SQLMap |
| Aplicar herramientas de análisis de seguridad | 11 herramientas reales integradas y operativas |
| Realizar pruebas de penetración controladas | Metasploit (modo auxiliar) + Patator + InjectionScanner sobre 3 labs |
| Documentar hallazgos de seguridad | 4 formatos de reporte: HTML, PDF, JSON, CSV |
| Implementar medidas de seguridad en aplicaciones | Headers de seguridad en Next.js, validación de targets, autenticación por token |
| Aplicar metodologías de seguridad (OWASP, PTES) | Pipeline alineado con OWASP Testing Guide v4.2 y PTES |
| Desarrollar aplicaciones web (full-stack) | Backend Flask + Frontend Next.js + 11 módulos Python |
| Trabajar con contenedores Docker | 10 servicios en Docker Compose con redes, volúmenes y health checks |
| Gestionar bases de datos y persistencia | Redis para estado de escaneos, MariaDB para DVWA |
| Analizar y comunicar riesgos de seguridad | Sistema de scoring con 13 niveles + recomendaciones automáticas priorizadas |

### 17.2 Habilidades transversales demostradas

**Resolución de problemas técnicos complejos:** El proyecto documentó y resolvió más de 35 bugs técnicos concretos, incluyendo: el typo crítico en el auto-login de WebGoat (`securesacan` vs `securescan`), el token CSRF de dos etapas de DVWA, el renombre de `nikto_findings` a `nuclei_findings`, la corrección de la firma de `run_nuclei()`, y muchos más.

**Diseño de software con patrones de resiliencia:** Circuit Breaker en doble capa, timeout seguro con `threading.Event` (en lugar de `signal.SIGALRM` que no funciona en threads), retry con backoff exponencial, almacenamiento dual Redis/memoria.

**Desarrollo full-stack:** Desde la imagen Docker hasta la interfaz de usuario React, pasando por la API REST, el orquestador, los módulos de herramientas, el generador de reportes y el sistema de scoring.

**Escritura técnica:** 5 documentos técnicos (~100+ páginas de documentación total) con especificaciones exactas alineadas al código fuente real.

---

## 18. CONSIDERACIONES ÉTICAS Y LEGALES

### 18.1 Marco ético del proyecto

SecureScan Pro fue diseñado con ética como principio de diseño, no como complemento. El sistema implementa las siguientes salvaguardas técnicas:

**Validación estricta de targets:** La API rechaza cualquier IP o dominio que no sea un target del laboratorio o que no sea explícitamente permitido. No es posible usar el sistema para escanear objetivos reales sin modificar deliberadamente el código:

```python
FORBIDDEN_PATTERNS = [
    r'^localhost', r'^127\.', r'^0\.0\.0\.0',
    r'^10\.', r'^192\.168\.', r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',
    r'^::1', r'^fc00:', r'^fe80:',
]
```

**Modo restrictivo:** Activando `RESTRICT_TO_LAB_TARGETS=true` en `.env`, la API solo acepta exactamente los tres targets del laboratorio.

**Metasploit en modo auxiliar:** Solo se ejecutan módulos de verificación (`auxiliary/`), nunca módulos de explotación activa (`exploits/`) ni payloads maliciosos.

**Aislamiento de red:** Los containers del laboratorio están en una red Docker (`lab-net`) aislada del tráfico externo. No tienen salida a Internet.

### 18.2 Uso legal y autorizado

El análisis de seguridad sobre sistemas sin autorización expresa es un delito en Colombia bajo la Ley 1273 de 2009 (Ley de Delitos Informáticos) y en la mayoría de jurisdicciones internacionales.

SecureScan Pro solo debe ser operado sobre:
- Los laboratorios incluidos en el sistema (DVWA, Juice Shop, WebGoat).
- Sistemas propios en los que el operador tenga propiedad o autorización explícita por escrito.
- Entornos de prueba y laboratorio aislados creados específicamente para ese propósito.

### 18.3 Datos y privacidad

- Los resultados de los escaneos se almacenan localmente en Redis con un TTL de 24 horas para escaneos completados.
- No se envía ningún dato a servidores externos durante la operación normal.
- Los reportes generados pueden contener información sensible sobre la postura de seguridad del sistema analizado y deben tratarse con confidencialidad.

---

## 19. CONCLUSIONES

### 19.1 Conclusiones técnicas

**El pipeline secuencial es la aportación técnica central.** La integración de 11 herramientas en un flujo ordenado —donde cada herramienta alimenta a la siguiente— es lo que diferencia SecureScan Pro de una colección de scripts independientes. La propagación de cookies de sesión, la inyección de URLs de ffuf/Gobuster en ZAP, y la correlación automática de Searchsploit con los hallazgos de ZAP son ejemplos concretos de esta integración.

**El módulo InjectionScanner es la contribución de código más original.** Con 1.689 líneas de Python, 10 técnicas de inyección y 27 subtipos de detección, es el módulo más extenso del proyecto y el que más valor formativo aporta al demostrar cómo se implementa un escáner de vulnerabilidades desde cero.

**La resiliencia es tan importante como la funcionalidad.** Los 35+ bugs documentados y resueltos durante el desarrollo incluyen problemas de threading, timeouts en entornos multi-hilo, tokens CSRF de múltiples etapas y errores de nombrado entre módulos. El sistema final es robusto precisamente por haber enfrentado y resuelto cada uno de estos problemas.

### 19.2 Conclusiones formativas

El desarrollo de SecureScan Pro permitió aplicar en un contexto real e integrado todas las competencias del programa Técnico en Seguridad de Aplicaciones Web del SENA: desde el reconocimiento de infraestructura hasta la generación de reportes ejecutivos, pasando por el análisis dinámico de vulnerabilidades, las pruebas de penetración controladas y la documentación técnica.

La plataforma demuestra que es posible para un aprendiz del SENA construir herramientas de nivel profesional combinando conocimiento de ciberseguridad con habilidades de desarrollo de software.

### 19.3 Trabajo futuro

| Mejora propuesta | Impacto |
|---|---|
| Soporte multi-usuario con autenticación por roles | Permite uso en clases con múltiples aprendices |
| Integración de SAST (análisis estático de código) | Completaría el ciclo DAST + SAST |
| Exportación a formatos de ticketing (JIRA, GitHub Issues) | Integración con flujos DevSecOps reales |
| API pública documentada con Swagger/OpenAPI | Facilita integración con otras herramientas |
| Modo "hacking guide" con explicaciones por hallazgo | Valor educativo adicional para el laboratorio |
| Soporte para análisis de APIs GraphQL | Cubre tecnologías modernas como Juice Shop |

---

## 20. GLOSARIO DE TÉRMINOS TÉCNICOS

| Término | Definición |
|---|---|
| **API REST** | Interfaz de comunicación entre sistemas que usa el protocolo HTTP y formato JSON |
| **Circuit Breaker** | Patrón de software que evita llamadas repetidas a un servicio fallando |
| **CORS** | Cross-Origin Resource Sharing — mecanismo de seguridad de navegadores web |
| **CSRF** | Cross-Site Request Forgery — ataque que fuerza acciones no autorizadas en nombre del usuario |
| **CVE** | Common Vulnerabilities and Exposures — sistema de identificación de vulnerabilidades conocidas |
| **CVSS** | Common Vulnerability Scoring System — estándar de puntuación de severidad de vulnerabilidades |
| **DAST** | Dynamic Application Security Testing — prueba de seguridad sobre la aplicación en ejecución |
| **Docker Compose** | Herramienta para definir y ejecutar aplicaciones multi-contenedor |
| **ExploitDB** | Base de datos pública de exploits mantenida por Offensive Security |
| **Fingerprinting** | Técnica de identificación de tecnologías usadas por una aplicación web |
| **Flask** | Microframework web de Python para construir APIs REST |
| **Fuzzing** | Técnica de testing que envía entradas inesperadas o aleatorias para encontrar fallos |
| **Health Check** | Verificación periódica del estado operativo de un servicio |
| **JWT** | JSON Web Token — estándar para tokens de autenticación sin estado |
| **LFI** | Local File Inclusion — vulnerabilidad que permite leer archivos del servidor |
| **Next.js** | Framework React para aplicaciones web con renderizado en servidor (SSR) |
| **Nuclei** | Escáner de vulnerabilidades basado en plantillas YAML de la comunidad |
| **OWASP** | Open Worldwide Application Security Project — organización referente en seguridad web |
| **Orquestador** | Componente que coordina la ejecución de múltiples herramientas o servicios |
| **Pentest** | Penetration Testing — prueba de penetración autorizada para encontrar vulnerabilidades |
| **Pipeline** | Secuencia ordenada de pasos donde la salida de cada uno alimenta al siguiente |
| **Payload** | Datos enviados como parte de un ataque o prueba de seguridad |
| **Redis** | Base de datos en memoria tipo clave-valor usada para caché y sesiones |
| **SAST** | Static Application Security Testing — análisis de código fuente sin ejecución |
| **SQLi** | SQL Injection — inyección de código SQL en parámetros de una aplicación |
| **SSRF** | Server-Side Request Forgery — fuerza al servidor a hacer peticiones a recursos internos |
| **SSTI** | Server-Side Template Injection — inyección en motores de plantillas del servidor |
| **TTL** | Time To Live — tiempo de vida de un dato en caché antes de ser eliminado |
| **Threading** | Ejecución concurrente de múltiples tareas en un mismo proceso |
| **Timeout** | Tiempo máximo de espera antes de cancelar una operación |
| **UUID** | Universally Unique Identifier — identificador único global (versión v4 en este proyecto) |
| **Wappalyzer** | Herramienta de identificación del stack tecnológico de sitios web |
| **XSS** | Cross-Site Scripting — inyección de scripts maliciosos en páginas web |
| **XXE** | XML External Entity — vulnerabilidad en parsers XML mal configurados |

---

## 21. REFERENCIAS

### Estándares y metodologías

- OWASP Foundation. (2021). *OWASP Top 10 2021*. https://owasp.org/Top10/
- OWASP Foundation. (2021). *OWASP Web Security Testing Guide v4.2*. https://owasp.org/www-project-web-security-testing-guide/
- PTES Technical Guidelines. (2012). *Penetration Testing Execution Standard*. http://www.pentest-standard.org/
- NIST. (2019). *Common Vulnerability Scoring System v3.1: Specification Document*. https://www.first.org/cvss/v3.1/specification-document
- MITRE Corporation. (2023). *Common Weaknesses Enumeration (CWE)*. https://cwe.mitre.org/

### Herramientas integradas — Documentación oficial

- Nmap Project. *Nmap Network Scanner*. https://nmap.org/docs.html
- OWASP ZAP. *OWASP Zed Attack Proxy*. https://www.zaproxy.org/docs/
- ProjectDiscovery. *Nuclei v3 Documentation*. https://docs.projectdiscovery.io/tools/nuclei/
- sqlmapproject. *sqlmap: Automatic SQL injection tool*. https://sqlmap.org/
- OJ Reeves. *Gobuster*. https://github.com/OJ/gobuster
- ffuf Project. *ffuf - Fuzz Faster U Fool*. https://github.com/ffuf/ffuf
- Metasploit Framework. *Metasploit Documentation*. https://docs.metasploit.com/
- Offensive Security. *Exploit Database — Searchsploit*. https://www.exploit-db.com/searchsploit
- lanjelot. *Patator: A multi-purpose brute-forcer*. https://github.com/lanjelot/patator

### Laboratorios de seguridad

- Bjoern Kimminich. *OWASP Juice Shop*. https://owasp.org/www-project-juice-shop/
- Ryan Dewhurst. *DVWA - Damn Vulnerable Web Application*. https://github.com/digininja/DVWA
- WebGoat Project. *WebGoat: A deliberately insecure application*. https://owasp.org/www-project-webgoat/

### Tecnologías de desarrollo

- Vercel. *Next.js 14 Documentation*. https://nextjs.org/docs
- Pallets Projects. *Flask 3.x Documentation*. https://flask.palletsprojects.com/
- Python Software Foundation. *Python 3.11 Documentation*. https://docs.python.org/3.11/
- Redis Ltd. *Redis 7 Documentation*. https://redis.io/docs/
- Docker Inc. *Docker Compose Documentation*. https://docs.docker.com/compose/
- shadcn. *shadcn/ui Components*. https://ui.shadcn.com/

### Legislación colombiana

- Congreso de Colombia. (2009). *Ley 1273 de 2009 — Delitos Informáticos*. https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=34492
- Congreso de Colombia. (2012). *Ley 1581 de 2012 — Protección de Datos Personales*. https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981

---

*Documento presentado como parte del Proyecto de Grado del programa Técnico en Seguridad de Aplicaciones Web.*  
*SENA — Servicio Nacional de Aprendizaje — Colombia, 2026*  
*SecureScan Pro v3.0 — Backend v5.0 — Dockerfile v3.1.3*
