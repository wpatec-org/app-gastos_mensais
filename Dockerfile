FROM python:3.10-slim

# Instala dependências do sistema para WeasyPrint
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    shared-mime-info \
    mime-support \
    fonts-dejavu \
    fonts-liberation \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código fonte (preserva a pasta relatorios existente)
COPY --chown=appuser:appuser . .

# Configura usuário não-root
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app
USER appuser

# Documenta o volume
VOLUME /app/relatorios

EXPOSE 5000

CMD ["/usr/local/bin/gunicorn", "--bind", "0.0.0.0:5000", "app:app"]