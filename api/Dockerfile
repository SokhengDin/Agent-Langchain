FROM python:3.14-alpine

WORKDIR /app

# Install build dependencies and runtime libraries
RUN apk add --no-cache \
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
    libgeos-dev \
    curl \
    && rm -rf /var/cache/apk/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:/root/.local/bin:$PATH"

# Copy dependency files
COPY pyproject.toml ./
COPY README.md ./

# Install Python dependencies
RUN uv pip install --system --no-cache .

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

EXPOSE 8000

CMD ["fastapi", "run", "main.py", "--port", "8000", "--proxy-headers"]