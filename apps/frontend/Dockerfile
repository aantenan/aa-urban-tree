FROM node:20-alpine AS builder

WORKDIR /app

COPY apps/frontend/package.json apps/frontend/package-lock.json* ./
RUN npm ci 2>/dev/null || npm install

COPY apps/frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
