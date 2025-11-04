FROM node:20-alpine AS deps
WORKDIR /app

COPY package.json ./
RUN npm install --legacy-peer-deps

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED 1
ENV NODE_ENV production

RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app

# Accept user and group ID as build arguments
ARG USER_ID=1000
ARG GROUP_ID=1000

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# Create a non-root user with the specified UID/GID
RUN if [ "$USER_ID" != "0" ]; then \
        addgroup -g ${GROUP_ID} appgroup 2>/dev/null || true; \
        adduser -D -u ${USER_ID} -G appgroup appuser 2>/dev/null || true; \
    fi

# Copy public folder
COPY --from=builder /app/public ./public

# Copy standalone directory and set ownership
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Set proper permissions
RUN if [ "${USER_ID}" != "0" ]; then \
        chown -R ${USER_ID}:${GROUP_ID} /app; \
    fi

EXPOSE 3000

ENV HOSTNAME "0.0.0.0"
ENV PORT 3000

CMD ["node", "server.js"]