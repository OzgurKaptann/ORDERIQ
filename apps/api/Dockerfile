FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure media directory exists in the image
RUN mkdir -p media/qr

EXPOSE 8000

# Run migrations then start server.
# --reload enables hot reloading when the source is bind-mounted for local dev.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
