FROM python:3.10-slim

WORKDIR /opt/user_service

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=$PYTHONPATH:.

RUN mkdir -p /app && chmod 777 /app

COPY user_service /opt/user_service/user_service

CMD ["uvicorn", "user_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
