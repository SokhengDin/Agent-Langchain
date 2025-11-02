FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libpq-dev \
        patch \
        libc6-dev \
        linux-libc-dev \
        libffi-dev \
        libcairo2-dev \
        libpango1.0-dev \
        libgdk-pixbuf-xlib-2.0-dev \
        shared-mime-info \
        libgirepository1.0-dev \
        libgl1-mesa-dev \
        libgomp1 \
        libgeos-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install aiohttp python-multipart

COPY . .

EXPOSE 8005

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"]