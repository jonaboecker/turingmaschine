FROM python:3.12-slim
LABEL authors="jonab"

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
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Öffne den Standard-Port für Flask
EXPOSE 5000

# Starte die Flask-Anwendung
CMD ["flask", "run"]
