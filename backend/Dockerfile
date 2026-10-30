FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api ./api
COPY ocr_indexer ./ocr_indexer

EXPOSE 8500

CMD ["python", "-m", "uvicorn", "api.main:app", "--root-path", "/api", "--port", "8500", "--host", "0.0.0.0"]
