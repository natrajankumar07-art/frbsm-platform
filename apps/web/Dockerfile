FROM node:20-slim AS base
WORKDIR /app

# ── deps ──────────────────────────────────────────────────────────────────────
FROM base AS deps
COPY apps/web/package.json apps/web/package-lock.json ./apps/web/
WORKDIR /app/apps/web
RUN npm ci --prefer-offline

# ── development ───────────────────────────────────────────────────────────────
FROM deps AS development
COPY apps/web/ /app/apps/web/
EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--host"]

# ── builder ───────────────────────────────────────────────────────────────────
FROM deps AS builder
COPY apps/web/ /app/apps/web/
RUN npm run build

# ── production ────────────────────────────────────────────────────────────────
FROM nginx:1.27-alpine AS production
COPY --from=builder /app/apps/web/dist /usr/share/nginx/html
COPY apps/web/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD wget -q -O - http://localhost/health || exit 1
