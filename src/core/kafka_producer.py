import json
from confluent_kafka import Producer
from src.utils.config import Config

class KafkaProducerManager:
    def __init__(self):
        self.conf = {
            'bootstrap.servers': Config.KAFKA_BOOTSTRAP_SERVERS,
            'client.id': 'rag-api-producer'
        }
        self.producer = Producer(self.conf)

    def delivery_report(self, err, msg):
        """Called once for each message produced to indicate delivery result."""
        if err is not None:
            print(f'Message delivery failed: {err}')
        else:
            print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    def send_message(self, topic, data):
        """Send a JSON message to a Kafka topic."""
        self.producer.produce(
            topic, 
            key=data.get('filename', 'unknown'), 
            value=json.dumps(data), 
            callback=self.delivery_report
        )
        # Wait for any outstanding messages to be delivered
        self.producer.flush()
