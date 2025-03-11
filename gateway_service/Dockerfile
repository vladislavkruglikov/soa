FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY gateway_service/ ./gateway_service

CMD ["uvicorn", "gateway_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
