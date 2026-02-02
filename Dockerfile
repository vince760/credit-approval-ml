FROM node:20-alpine AS frontend
WORKDIR /fe

COPY frontend/package*.json ./
RUN npm ci

COPY frontend ./
RUN npm run build && npx next export


FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# App + model artifacts
COPY backend /app/backend
COPY artifacts /app/artifacts

# Copy exported frontend into the image where Flask will serve it from
COPY --from=frontend /fe/out /app/frontend/out

EXPOSE 5000

CMD ["sh", "-c", "gunicorn -w 2 -b 0.0.0.0:${PORT:-5000} backend.app:app"]
