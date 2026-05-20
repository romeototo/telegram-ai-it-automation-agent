FROM python:3.11-slim

LABEL maintainer="RoMEoTOTO <romeototo@github>"
LABEL description="Telegram AI IT Automation Agent"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping \
    procps \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs data

# Run the bot
CMD ["python", "-m", "src.main"]
