# Frontend Dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend .
# Pass API base at build time so Vite embeds it correctly
ARG VITE_API_BASE
ENV VITE_API_BASE=${VITE_API_BASE}
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
# Simple default nginx config
RUN sed -i 's@/var/www/html@/usr/share/nginx/html@g' /etc/nginx/conf.d/default.conf || true
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
