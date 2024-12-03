FROM python:3.12-slim-bullseye
LABEL authors="jonab"

# Installiere System-Abhängigkeiten
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Setze ein Arbeitsverzeichnis im Container
WORKDIR /app

# Kopiere die Abhängigkeitsdatei
COPY requirements.txt requirements.txt

# Installiere die Abhängigkeiten
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Kopiere den restlichen Code ins Arbeitsverzeichnis
COPY . .

# Setze die Umgebungsvariable für Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Öffne den Standard-Port für Flask
EXPOSE 5000

# Starte die Anwendung mit Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
