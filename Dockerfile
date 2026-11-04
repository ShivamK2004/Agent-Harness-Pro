
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data logs workspace

EXPOSE 8000

CMD ["sh", "-c", "uvicorn harness.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
