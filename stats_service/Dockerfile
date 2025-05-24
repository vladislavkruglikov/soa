FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY stats.proto .
RUN python -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    stats.proto

COPY . .

ENV PYTHONPATH=$PYTHONPATH:.

CMD ["python", "server.py"] 