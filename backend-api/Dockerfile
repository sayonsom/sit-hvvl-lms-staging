FROM python:3.11-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Update apt-get and install packages
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    unixodbc-dev \
    ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set work directory for our application
WORKDIR /code

# Upgrade pip and install Python dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . /code

# Use shell so ${PORT} expands at runtime. Single worker for in-memory LTI state.
CMD ["sh", "-c", "gunicorn -w 1 -k uvicorn.workers.UvicornWorker -t 3000 --bind 0.0.0.0:${PORT:-8080} main:app"]

# Cloud Run listens on $PORT (default 8080)
EXPOSE 8080
