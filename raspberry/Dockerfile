FROM balenalib/raspberry-pi-debian-python:latest

LABEL authors="jonab"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    python3-serial \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

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
