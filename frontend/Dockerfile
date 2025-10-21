# AgentHub/frontend/Dockerfile

# Builder Stage
FROM node:20-alpine AS builder
WORKDIR /app

# docker-compose.yml の build.args から変数を受け取る
ARG NEXT_PUBLIC_API_URL
ARG API_URL_INTERNAL

COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Runner Stage
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]