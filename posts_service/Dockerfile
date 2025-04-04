FROM python:3.9-slim

WORKDIR /opt/posts_service

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /opt/posts_service/posts_service

ENV PYTHONPATH=$PYTHONPATH:.

EXPOSE 50051

CMD ["python", "/opt/posts_service/posts_service/server.py"]
