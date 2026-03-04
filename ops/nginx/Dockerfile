FROM node:20-alpine AS web-build
WORKDIR /app

COPY apps/web/package*.json ./
RUN npm ci
COPY apps/web/ ./
RUN npm run build

FROM nginx:1.27-alpine
RUN mkdir -p /var/www/certbot
COPY ops/nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=web-build /app/dist /usr/share/nginx/html
