FROM python:3.12-slim-bullseye
LABEL authors="jonab"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Falls wiringpi nicht per apt installierbar ist, baue es manuell
RUN if ! command -v gpio &> /dev/null; then \
    git clone https://github.com/WiringPi/WiringPi.git /tmp/wiringpi \
    && cd /tmp/wiringpi \
    && sed -i 's/sudo //g' build \
    && sed -i 's/uninstall/true/g' build \
    && chmod +x build \
    && ./build \
    && rm -rf /tmp/wiringpi; \
    fi

# Set a working directory in the container
WORKDIR /app

# Copy the dependency file
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code into the working directory
COPY . .

# Set the environment variable for Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Open the default port for Flask
EXPOSE 5000

# Start the application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
