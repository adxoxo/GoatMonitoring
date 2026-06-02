# Frontend image — build the SPA, then publish dist/ into a shared volume
# that the Nginx service serves (see docker-compose.yml). The container runs
# once, copies the build output, and exits 0.
FROM node:24-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Minimal final stage: hold the built assets and copy them into the mounted
# `frontend_dist` volume on start.
FROM alpine:3.20

WORKDIR /app
COPY --from=build /app/dist /app/dist

# /dist is the mount point for the shared volume Nginx reads from.
CMD ["sh", "-c", "cp -r /app/dist/. /dist/ && echo 'Frontend build published to volume.'"]
