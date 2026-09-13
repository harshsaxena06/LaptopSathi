FROM node:20-alpine AS build
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

# Empty string = "call the API on this same origin" (e.g. /api/search), which
# nginx.conf below reverse-proxies to the backend container. This avoids the
# browser needing CORS at all in the docker-compose deployment. Override with
# --build-arg VITE_API_BASE_URL=https://api.example.com for a split deployment
# (frontend and backend on different hosts) instead.
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost/ >/dev/null || exit 1
