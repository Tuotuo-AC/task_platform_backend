import redis
from app.core.config import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def publish_notification(channel: str, message: str):
    redis_client.publish(channel, message)