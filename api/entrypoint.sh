#!/bin/sh
set -e

# Create logs directory if it doesn't exist
mkdir -p /app/logs

# Ensure proper permissions for the current user
if [ -w /app/logs ]; then
    chmod -R u+w /app/logs 2>/dev/null || true
fi

# Execute the main command
exec "$@"
