FROM python:3.11-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    && rm -rf /var/cache/apk/*

# Create working directory
WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S python \
    && adduser -u 1001 -S python -G python

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Change ownership to python user
RUN chown -R python:python /app

# Switch to non-root user
USER python

# Expose port
EXPOSE 8004

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]