from kafka import KafkaProducer
import json
from datetime import datetime

KAFKA_BOOTSTRAP_SERVERS = 'kafka:29092'
POST_LIKE_TOPIC = 'post_likes'
POST_VIEW_TOPIC = 'post_views'
POST_COMMENT_TOPIC = 'post_comments'

def get_kafka_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

def send_post_like_event(producer, user_id: int, post_id: int, action_time: datetime):
    event = {
        'user_id': user_id,
        'post_id': post_id,
        'action_time': action_time.isoformat(),
        'event_type': 'post_like'
    }
    producer.send(POST_LIKE_TOPIC, event)
    producer.flush()

def send_post_view_event(producer, user_id: int, post_id: int, action_time: datetime):
    event = {
        'user_id': user_id,
        'post_id': post_id,
        'action_time': action_time.isoformat(),
        'event_type': 'post_view'
    }
    producer.send(POST_VIEW_TOPIC, event)
    producer.flush()

def send_post_comment_event(producer, user_id: int, post_id: int, comment_id: int, action_time: datetime):
    event = {
        'user_id': user_id,
        'post_id': post_id,
        'comment_id': comment_id,
        'action_time': action_time.isoformat(),
        'event_type': 'post_comment'
    }
    producer.send(POST_COMMENT_TOPIC, event)
    producer.flush() 