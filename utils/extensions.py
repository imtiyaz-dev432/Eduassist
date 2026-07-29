from redis import Redis
from config import Config

redis_client=Redis.from_url(
    Config.REDIS_URL,
    decode_responses=True
)