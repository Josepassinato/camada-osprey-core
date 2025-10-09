# Multi-stage build for React Frontend
FROM node:18-alpine AS builder

# Metadata
LABEL maintainer="OSPREY Support <support@osprey.com>"
LABEL description="OSPREY Immigration Platform Frontend"
LABEL version="2.0.0"

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile --production=false

# Copy source code
COPY . .

# Build the application
RUN yarn build

# Production stage
FROM nginx:alpine

# Copy built assets from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create non-root user
RUN addgroup -g 1001 -S osprey && \
    adduser -S osprey -u 1001 -G osprey

# Set proper permissions
RUN chown -R osprey:osprey /usr/share/nginx/html && \
    chown -R osprey:osprey /var/cache/nginx && \
    chown -R osprey:osprey /var/log/nginx && \
    chown -R osprey:osprey /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R osprey:osprey /var/run/nginx.pid

# Switch to non-root user
USER osprey

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# Expose port
EXPOSE 3000

# Start nginx
CMD ["nginx", "-g", "daemon off;"]