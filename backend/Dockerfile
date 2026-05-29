# FROM python:3.11-slim

# WORKDIR /app

# COPY requirements.txt .

# # Install CPU-only torch first
# RUN pip install --no-cache-dir torch \
# --index-url https://download.pytorch.org/whl/cpu

# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.11-slim

WORKDIR /app

# 🔥 Create a non-privileged system user account and group
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

COPY requirements.txt .

# Install CPU-only torch first
RUN pip install --no-cache-dir torch \
    --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 🔥 Create the storage directory explicitly and hand ownership over to appuser
# This ensures that when volumes mount, permissions don't fall back to root
RUN mkdir -p /app/chroma_storage && chown -R appuser:appuser /app

# 🔥 Drop privileges down to the non-root identity
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]