# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    chromium-driver \
    chromium \
    libnss3 \
    libgconf-2-4 \
    libxi6 \
    libgdk-pixbuf2.0-0 \
    libatk1.0-0 \
    libgtk-3-0 \
    libasound2 \
    fonts-liberation \
    libappindicator3-1 \
    libnspr4 \
    xdg-utils \
    wget \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your bot's code
COPY . /app
WORKDIR /app

# Run your bot
CMD ["python", "main.py"]
