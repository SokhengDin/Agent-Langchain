FROM python:3.12-alpine

WORKDIR /app

# Install build dependencies and runtime libraries
RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    postgresql-dev \
    libffi-dev \
    gdk-pixbuf-dev \
    shared-mime-info \
    gobject-introspection-dev \
    mesa-dev \
    geos-dev \
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

EXPOSE 8005

CMD ["fastapi", "run", "main.py", "--port", "8005", "--proxy-headers"]