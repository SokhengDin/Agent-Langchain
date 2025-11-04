#!/bin/bash
set -e

# Create upload directories if they don't exist
mkdir -p /app/uploads/images
mkdir -p /app/uploads/documents
mkdir -p /app/uploads/data
mkdir -p /app/logs
mkdir -p /app/output

# Ensure proper permissions for the current user
# This handles cases where volumes are mounted and owned by root
if [ -w /app/uploads ]; then
    chmod -R u+w /app/uploads /app/logs /app/output 2>/dev/null || true
fi

# Execute the main command
exec "$@"
