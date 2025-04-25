FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY gateway_service/post.proto ./gateway_service/
RUN python -m grpc_tools.protoc \
    -I./gateway_service \
    --python_out=./gateway_service \
    --grpc_python_out=./gateway_service \
    ./gateway_service/post.proto

COPY gateway_service/ ./gateway_service

ENV PYTHONPATH=$PYTHONPATH:.
ENV PYTHONPATH=$PYTHONPATH:./gateway_service

CMD ["uvicorn", "gateway_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
