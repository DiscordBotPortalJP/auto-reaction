import motor.motor_asyncio
from caches import emojis_cache
from constants import MONGO_URL

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
database = client.auto_reaction
# database_emojis = database.emojis


async def cache_emojis() -> None:
    async for emojis in database.emojis.find():
        channel_id = emojis.get('channel_id')
        emojis = emojis.get('emojis')
        emojis_cache[channel_id] = emojis


def get_emojis(channel_id: int) -> dict | None:
    return emojis_cache.get(channel_id)


async def upsert_emojis(channel_id: int, emojis: list[str]) -> bool:
    query = {'channel_id': channel_id}
    values = {
        'channel_id': channel_id,
        'emojis': emojis,
    }
    await database.emojis.update_one(query, {'$set': values}, upsert=True)
    emojis_cache[channel_id] = emojis


async def delete_emojis(channel_id):
    result = await database.emojis.delete_one({'channel_id': channel_id})
    if result.deleted_count > 0:
        emojis_cache.pop(channel_id, None)
