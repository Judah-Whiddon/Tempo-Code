# TempoCode frontend (dev mode) — Vite hot reload inside the container.
# Source is mounted from the host via docker-compose so edits are live.
# An anonymous volume on /app/node_modules in compose protects the
# container's installed deps from being shadowed by the host mount.

FROM node:20-alpine

WORKDIR /app

# Install deps before copying source — speeds up rebuilds on source-only changes.
COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 3000

# --host 0.0.0.0 makes the dev server reachable from outside the container.
# vite.config.js already sets port 3000.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
