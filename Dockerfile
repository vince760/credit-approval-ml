FROM python:3.11-slim

# xgboost runtime dependency
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first (better build caching)
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend code + artifacts (model.pkl is required)
COPY backend /app/backend
COPY artifacts /app/artifacts

EXPOSE 5000

# Run API in production mode
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "backend.app:app"]
