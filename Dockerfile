# Use a lightweight Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Create a non-root user with UID 568
RUN useradd -u 568 -m -s /bin/bash appuser

# Copy requirements.txt first to leverage Docker caching
COPY requirements.txt .

# Install dependencies as root, then clean up
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache

# Copy the rest of the application files
COPY . .

# Change ownership of the app directory to appuser
RUN chown -R appuser:appuser /app

# Switch to the non-root user (UID 568)
USER appuser

# Expose the port the app runs on
EXPOSE 5000

# Run the app as appuser
CMD ["python", "symlink_cleaner.py", "--config", "config.json"]