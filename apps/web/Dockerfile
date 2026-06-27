FROM node:20-slim AS base
RUN corepack enable && corepack prepare pnpm@latest --activate
WORKDIR /app

# ── deps ──────────────────────────────────────────────────────────────────────
FROM base AS deps
COPY pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/web/package.json ./apps/web/
RUN pnpm install --frozen-lockfile

# ── development ───────────────────────────────────────────────────────────────
FROM deps AS development
COPY apps/web/ ./apps/web/
WORKDIR /app/apps/web
EXPOSE 3000
CMD ["pnpm", "dev", "--host"]

# ── builder ───────────────────────────────────────────────────────────────────
FROM deps AS builder
COPY apps/web/ ./apps/web/
WORKDIR /app/apps/web
RUN pnpm build

# ── production ────────────────────────────────────────────────────────────────
FROM nginx:1.27-alpine AS production
COPY --from=builder /app/apps/web/dist /usr/share/nginx/html
COPY apps/web/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD wget -q -O - http://localhost/health || exit 1
