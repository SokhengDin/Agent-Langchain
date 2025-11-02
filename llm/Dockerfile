FROM python:3.12-slim

WORKDIR /app

# Install build dependencies and runtime libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libgdk-pixbuf-xlib-2.0-dev \
    shared-mime-info \
    libgirepository1.0-dev \
    libgl1-mesa-dev \
    libgeos-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Install uv (Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:/root/.local/bin:$PATH"

COPY pyproject.toml README.md ./

RUN uv pip install --system --no-cache torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1

# Install all project dependencies
RUN uv pip install --system --no-cache .

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

EXPOSE 8005

CMD ["fastapi", "run", "main.py", "--port", "8005", "--proxy-headers"]
