FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libpq-dev \
        libc6-dev \
        linux-libc-dev \
        libffi-dev \
        libgdk-pixbuf-xlib-2.0-dev \
        shared-mime-info \
        libgirepository1.0-dev \
        libgl1-mesa-dev \
        libgomp1 \
        libgeos-dev \
        curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:/root/.local/bin:$PATH"

COPY pyproject.toml ./
COPY README.md ./

RUN uv sync --locked

COPY . .

RUN mkdir -p /app/logs

EXPOSE 8000

CMD ["fastapi", "run", "main.py", "--port", "8000", "--proxy-headers"]