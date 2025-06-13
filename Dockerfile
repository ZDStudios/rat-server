FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for evdev and pip
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-pip \
    gcc \
    python3-dev \
    libevdev-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python -m pip install --upgrade pip

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

CMD ["python", "server.py"]
