# Stage 1: Build the application
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies first (leverage Docker caching)
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Copy the rest of the application files
COPY frontend/ ./

# Define relative API URL environment variable for host-agnostic deployment via Nginx reverse proxy
ENV NEXT_PUBLIC_API_URL=/api
ENV NODE_ENV=production

# Build the Next.js app
RUN npm run build

# Stage 2: Production runner
FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Copy package files and install production dependencies
COPY --from=builder /app/package.json /app/package-lock.json ./
RUN npm ci --only=production

# Copy built artifacts and public resources
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/styles ./styles

EXPOSE 3000

CMD ["npm", "run", "start"]
