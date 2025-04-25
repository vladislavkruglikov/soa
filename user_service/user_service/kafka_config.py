from kafka import KafkaProducer
import json
from datetime import datetime

KAFKA_BOOTSTRAP_SERVERS = 'kafka:29092'
USER_REGISTRATION_TOPIC = 'user_registrations'

def get_kafka_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

def send_user_registration_event(producer, user_id: int, registration_date: datetime):
    event = {
        'user_id': user_id,
        'registration_date': registration_date.isoformat(),
        'event_type': 'user_registered'
    }
    producer.send(USER_REGISTRATION_TOPIC, event)
    producer.flush() 