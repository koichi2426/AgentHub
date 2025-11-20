# AgentHub/frontend/Dockerfile

# Builder Stage
FROM node:24-alpine AS builder
WORKDIR /app
RUN apk add --no-cache libc6-compat

# docker-compose.yml の build.args から変数を受け取る
ARG NEXT_PUBLIC_API_URL
ARG API_URL_INTERNAL

COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Runner Stage
FROM node:24-alpine AS runner
WORKDIR /app
RUN apk add --no-cache libc6-compat
ENV NODE_ENV=production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]