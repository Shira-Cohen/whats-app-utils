import os
from typing import List

import redis.asyncio as redis
from datetime import timedelta
import json
from sqlalchemy.inspection import inspect
from datetime import datetime, date

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

MAX_MESSAGES = 20  # amount of saved messages

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    db=0
)


async def set_cache_conversation(conversation: dict, ttl_seconds: int = 3600):
    key = f"conversation:{conversation['id']}"
    await redis_client.set(key, json.dumps(conversation), ex=ttl_seconds)


async def get_cache_conversation(conversation_id: int) -> dict:
    key = f"conversation:{conversation_id}"
    conversation = await redis_client.get(key)
    return None if conversation is None else json.loads(conversation)


async def add_cache_message(conversation_id: int, message: dict, ttl_seconds: int = 3600):
    key = f"conversation:{conversation_id}:messages"
    await redis_client.lpush(key, json.dumps(message))
    await redis_client.ltrim(key, 0, MAX_MESSAGES - 1)
    await redis_client.expire(key, ttl_seconds)  # Set expiration time


def add_cache_message_sync(conversation_id: int, message: dict, ttl_seconds: int = 3600):
    key = f"conversation:{conversation_id}:messages"
    redis_client.lpush(key, json.dumps(message))
    redis_client.ltrim(key, 0, MAX_MESSAGES - 1)
    redis_client.expire(key, ttl_seconds)  # Set expiration time



async def add_cache_messages(conversation_id: int, messages: List[dict]):
    key = f"conversation:{conversation_id}:messages"

    # parse all messages to json
    messages_json = [json.dumps(msg) for msg in messages]
    # push all together
    if messages_json:
        await redis_client.lpush(key, *messages_json)
        await redis_client.ltrim(key, 0, MAX_MESSAGES - 1)


async def get_cached_messages_by_conversation(conversation_id: int) -> List[dict]:
    key = f"conversation:{conversation_id}:messages"
    messages = await redis_client.lrange(key, 0, -1)
    return [json.loads(m) for m in messages]


def sqlalchemy_obj_to_dict(obj) -> dict:
    result = {}
    for c in inspect(obj).mapper.column_attrs:
        value = getattr(obj, c.key)
        if isinstance(value, (datetime, date)):
            result[c.key] = value.isoformat()
        else:
            result[c.key] = value
    return result


# -----------------------------
# 👥 Participants in Conversations
# -----------------------------

def get_conversation_participants_key(conversation_id: int) -> str:
    return f"conversation:{conversation_id}:participants"


async def set_conversation_participants(conversation_id: int, participant_ids: List[int], ttl_seconds: int = 3600):
    """
    Saves a list of user IDs for a specific conversation (to a set).
    """
    key = get_conversation_participants_key(conversation_id)
    if participant_ids:
        await redis_client.sadd(key, *participant_ids)
        await redis_client.expire(key, ttl_seconds)


async def get_conversation_participants(conversation_id: int) -> List[int]:
    """
    Retrieves user IDs associated with a conversation.
    """
    key = get_conversation_participants_key(conversation_id)
    ids = await redis_client.smembers(key)
    return [int(pid) for pid in ids]


async def add_participant_to_conversation(conversation_id: int, participant_id: int):
    """
    Adds a new participant to an existing conversation.
    """
    key = get_conversation_participants_key(conversation_id)
    await redis_client.sadd(key, participant_id)


async def remove_participant_from_conversation(conversation_id: int, participant_id: int):
    """
    Removes a participant from a conversation.
    """
    key = get_conversation_participants_key(conversation_id)
    await redis_client.srem(key, participant_id)


async def get_cache_user(user_id: int) -> dict:
    """
    Retrieves cached user data from Redis.
    """
    key = f"user:{user_id}"
    user_data = await redis_client.get(key)
    return None if user_data is None else json.loads(user_data)


async def set_cache_user(user_id: int, user_data: dict, ttl_seconds: int = 3600):
    """
    Saves user data in Redis with an expiration time.
    """
    key = f"user:{user_id}"
    await redis_client.set(key, json.dumps(user_data), ex=ttl_seconds)


async def delete_cache_user(user_id: int):
    """
    Deletes user data from Redis.
    """
    key = f"user:{user_id}"
    await redis_client.delete(key)


def publish_ws_message(user_id: str, message: str):
    redis_client.publish("ws_channel", json.dumps({"user_id": user_id, "message": message}))