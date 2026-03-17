FROM python:3.11-slim

WORKDIR /app

# Dépendances en premier (optimise le cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code applicatif
COPY app/ ./app/

EXPOSE 5000

# Utilisateur non-root (sécurité obligatoire)
RUN adduser --disabled-password --gecos "" appuser
USER appuser

CMD ["python", "app/main.py"]