FROM python:3.12-slim

# Accept user and group ID as build arguments
ARG USER_ID=1000
ARG GROUP_ID=1000

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

# Create a non-root user with the specified UID/GID
RUN if [ "$USER_ID" != "0" ]; then \
        groupadd -g ${GROUP_ID} appgroup || true; \
        useradd -m -u ${USER_ID} -g appgroup appuser || true; \
    fi

# Install uv (Python package manager) as root
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:/root/.local/bin:$PATH"

COPY pyproject.toml README.md ./

RUN uv pip install --system --no-cache torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1

# Install all project dependencies
RUN uv pip install --system --no-cache .

# Copy application code
COPY . .

# Copy and set up entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create logs and output directories and set permissions
RUN mkdir -p /app/logs /app/output /app/uploads && \
    if [ "${USER_ID}" != "0" ]; then \
        chown -R ${USER_ID}:${GROUP_ID} /app; \
    fi

EXPOSE 8005

ENTRYPOINT ["/entrypoint.sh"]
CMD ["fastapi", "run", "main.py", "--port", "8005", "--proxy-headers"]
