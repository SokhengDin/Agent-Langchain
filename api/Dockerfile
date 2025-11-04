FROM python:3.14-alpine

# Accept user and group ID as build arguments
ARG USER_ID=1000
ARG GROUP_ID=1000

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
    shadow \
    && rm -rf /var/cache/apk/*

# Create a non-root user with the specified UID/GID
RUN if [ "$USER_ID" != "0" ]; then \
        addgroup -g ${GROUP_ID} appgroup || true; \
        adduser -D -u ${USER_ID} -G appgroup appuser || true; \
    fi

# Install uv as root
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:/root/.local/bin:$PATH"

# Copy dependency files
COPY pyproject.toml ./
COPY README.md ./

# Install Python dependencies
RUN uv pip install --system --no-cache .

# Copy application code
COPY . .

# Copy and set up entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create logs directory and set permissions
RUN mkdir -p /app/logs && \
    if [ "${USER_ID}" != "0" ]; then \
        chown -R ${USER_ID}:${GROUP_ID} /app; \
    fi

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["fastapi", "run", "main.py", "--port", "8000", "--proxy-headers"]
