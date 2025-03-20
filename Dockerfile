FROM golang:1.20 AS builder
WORKDIR /app
COPY . .
RUN go build -o symlink-cleaner

FROM debian:stable-slim
WORKDIR /root/
COPY --from=builder /app/symlink-cleaner .
COPY config.json .
CMD ["./symlink-cleaner"]
