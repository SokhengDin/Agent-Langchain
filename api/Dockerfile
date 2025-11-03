FROM python:3.14-alpine

WORKDIR /app

# Install build dependencies and runtime libraries (Alpine package names)
RUN apk add --no-cache \
    build-base \
    libpq-dev \
    patch \
    musl-dev \
    libffi-dev \
    cairo \
    cairo-dev \
    pango \
    pango-dev \
    gdk-pixbuf \
    gdk-pixbuf-dev \
    gobject-introspection \
    gobject-introspection-dev \
    shared-mime-info \
    mesa-dev \
    geos \
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

EXPOSE 8000

CMD ["fastapi", "run", "main.py", "--port", "8000", "--proxy-headers"]
