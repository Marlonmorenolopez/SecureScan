# ============================================================
# SecureScan Pro v3.1.3 — Dockerfile (backend API)
#
# CORRECCIONES:
#  1. Añadido wkhtmltopdf — requerido por pdfkit para generar PDFs
#  2. Gunicorn usa GUNICORN_TIMEOUT (env) — soporta escaneos >120s
#  3. Nuclei templates se copian/apuntan a /home/scanner/nuclei-templates
#     (coincide con el volumen del docker-compose)
#  4. Añadido gevent para workers async (maneja muchos escaneos concurrentes)
#  5. Añadido libcap2-bin para dar NET_RAW a nmap sin root completo
#  6. Script entrypoint.sh para inicialización robusta
# ============================================================

FROM python:3.11-slim-bookworm

LABEL maintainer="SecureScan Pro Team"
LABEL version="3.1.3"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONFAULTHANDLER=1

# ── Sistema base ─────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap \
    patator \
    curl \
    wget \
    ca-certificates \
    git \
    unzip \
    nodejs \
    npm \
    python3 \
    python3-pip \
    # BUG FIX: wkhtmltopdf es requerido por pdfkit para generar PDFs
    wkhtmltopdf \
    xvfb \
    # Para dar capacidades de red a nmap corriendo como usuario no-root
    libcap2-bin \
    && rm -rf /var/lib/apt/lists/*

# ── Go 1.22 (manual — golang-go de bookworm es 1.19, incompatible) ──
RUN curl -fsSL https://go.dev/dl/go1.22.5.linux-amd64.tar.gz \
    | tar -C /usr/local -xz
ENV GOPATH=/go
ENV PATH="/usr/local/go/bin:${GOPATH}/bin:/usr/local/bin:${PATH}"

# ── SQLMap ───────────────────────────────────────────────
RUN git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git /opt/sqlmap \
 && ln -s /opt/sqlmap/sqlmap.py /usr/local/bin/sqlmap \
 && ln -s /opt/sqlmap/sqlmapapi.py /usr/local/bin/sqlmapapi.py

# ── Herramientas Go ───────────────────────────────────────
# gobuster v3.6.0 (v3.8.2 requiere directiva 'tool' de Go 1.24)
# ffuf v2 requiere módulo path correcto: ffuf/v2
# nuclei v3.2.4 — versión estable probada
RUN go install github.com/OJ/gobuster/v3@v3.6.0 \
 && go install github.com/ffuf/ffuf/v2@v2.1.0 \
 && go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@v3.2.4 \
 && go clean -modcache || true \
 && cp /go/bin/gobuster /usr/local/bin/ \
 && cp /go/bin/ffuf     /usr/local/bin/ \
 && cp /go/bin/nuclei   /usr/local/bin/

# ── Wappalyzer ───────────────────────────────────────────
RUN pip install --no-cache-dir python-Wappalyzer requests beautifulsoup4

# ── Wordlists (SecLists) ──────────────────────────────────
RUN git clone --depth 1 https://github.com/danielmiessler/SecLists.git /opt/SecLists \
 && mkdir -p /usr/share/wordlists \
 && ln -s /opt/SecLists /usr/share/wordlists/seclists \
 && mkdir -p /usr/share/wordlists/dirb \
 && ln -s /opt/SecLists/Discovery/Web-Content/common.txt /usr/share/wordlists/dirb/common.txt

# ── Searchsploit ─────────────────────────────────────────
RUN git clone --depth 1 https://gitlab.com/exploit-database/exploitdb.git /opt/exploitdb \
 && ln -sf /opt/exploitdb/searchsploit /usr/local/bin/searchsploit

# ── Usuario ──────────────────────────────────────────────
RUN groupadd -r scanner && useradd -r -g scanner -d /home/scanner -m -s /bin/bash scanner

# BUG FIX: dar capacidades de red a nmap para que funcione sin root
RUN setcap cap_net_raw,cap_net_admin+eip /usr/bin/nmap || true

WORKDIR /app

# ── Python deps ──────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    # BUG FIX: gevent para workers async (escaneos concurrentes)
    && pip install --no-cache-dir gunicorn gevent

# ── App ──────────────────────────────────────────────────
COPY --chown=scanner:scanner . .
RUN chmod -R 755 /app

# ── Templates Nuclei ─────────────────────────────────────
# BUG FIX: path correcto — coincide con el volumen del docker-compose
USER root
RUN git clone --depth 1 https://github.com/projectdiscovery/nuclei-templates \
    /home/scanner/nuclei-templates \
    && chown -R scanner:scanner /home/scanner/nuclei-templates

# Permisos para nuclei config y templates
RUN mkdir -p /home/scanner/.config/nuclei \
    && echo "nuclei-templates-directory: /home/scanner/nuclei-templates" \
       > /home/scanner/.config/nuclei/config.yaml \
    && chown -R scanner:scanner /home/scanner/.config \
    && chown -R scanner:scanner /home/scanner/nuclei-templates \
    && chmod -R 755 /home/scanner/.config

# ── Directorio de reportes ────────────────────────────────
RUN mkdir -p /app/reports && chown -R scanner:scanner /app/reports

# ── Entrypoint script ─────────────────────────────────────
COPY --chown=scanner:scanner entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# ── Volver a usuario seguro ──────────────────────────────
USER scanner

# ── Wordlists propias del proyecto ──────────────────────────
COPY --chown=scanner:scanner wordlists/ /app/wordlists/
EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=5 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# timeout configurable vía env (default 3600s para escaneos largos)
# sync worker con threads — no requiere gevent, funciona en cualquier entorno
CMD ["sh", "-c", "\
    gunicorn \
    --bind              0.0.0.0:5000 \
    --workers           2 \
    --threads           4 \
    --worker-class      sync \
    --worker-tmp-dir    /dev/shm \
    --timeout           ${GUNICORN_TIMEOUT:-3600} \
    --graceful-timeout  30 \
    --keep-alive        5 \
    --log-level         info \
    --access-logfile    - \
    --error-logfile     - \
    app:app"]
