import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
import os 

rabbitmq_broker = RabbitmqBroker(
    url=os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/"),
    confirm_delivery=True,
)

dramatiq.set_broker(rabbitmq_broker)