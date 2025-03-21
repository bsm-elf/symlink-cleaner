FROM golang:1.20 AS builder
WORKDIR /app

# Copy module files first
COPY go.mod ./
# If you have go.sum, copy it as well:
# COPY go.sum ./

# Download dependencies
RUN go mod download

# Copy the rest of the project
COPY . .

# Ensure all dependencies are tidy (fetch new ones, including lumberjack)
RUN go mod tidy

# Build the Go application
RUN go build -o symlink-cleaner

FROM debian:stable-slim
WORKDIR /root/
COPY --from=builder /app/symlink-cleaner .
COPY config.json .
CMD ["./symlink-cleaner"]
