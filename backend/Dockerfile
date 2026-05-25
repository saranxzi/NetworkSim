# ---- Build stage ----
FROM python:3.12-slim AS builder

WORKDIR /build

# System deps for python-igraph C library
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ cmake pkg-config && \
    rm -rf /var/lib/apt/lists/*

# Install engine library first (changes less often)
COPY networksim_core/ /build/networksim_core/
RUN pip install --no-cache-dir /build/networksim_core[all]

# Install backend deps
COPY backend/requirements.txt /build/requirements.txt
RUN pip install --no-cache-dir -r /build/requirements.txt

# ---- Runtime stage ----
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY backend/app/ /app/app/

# Non-root user
RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
