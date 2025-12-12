from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL

client = AsyncIOMotorClient(MONGO_URL)
db = client.skill_swap_db

# Коллекции
users_collection = db.users          # Профили пользователей (рейтинг)
ads_collection = db.ads              # Объявления (учителя)
connections_collection = db.connections # История связей (для отзывов)

async def check_connection():
    try:
        await client.admin.command('ping')
        print("✅ Успешное подключение к MongoDB!")
    except Exception as e:
        print(f"❌ Ошибка БД: {e}")