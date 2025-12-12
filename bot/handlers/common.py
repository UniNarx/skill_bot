from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database.mongo import users_collection, ads_collection
from bot.keyboards import get_main_keyboard

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    user = message.from_user
    
    # Сохраняем пользователя (или обновляем)
    await users_collection.update_one(
        {"user_id": user.id},
        {"$set": {
            "username": user.username,
            "full_name": user.full_name
        }, "$setOnInsert": {"rating_sum": 0, "rating_count": 0}},
        upsert=True
    )
    
    welcome_text = (
        f"Привет, {user.full_name}! 👋\n\n"
        "Это платформа для обмена навыками.\n"
        "Вы можете найти учителя или стать им.\n\n"
        "⚠️ <b>Важно:</b> Убедитесь, что у вас установлен @username в настройках Telegram, иначе с вами не смогут связаться."
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

@router.message(F.text == "👤 Мой профиль")
async def my_profile(message: types.Message):
    user_id = message.from_user.id
    user = await users_collection.find_one({"user_id": user_id})
    my_ads = await ads_collection.count_documents({"author_id": user_id, "is_active": True})
    
    rating = 0.0
    if user.get("rating_count", 0) > 0:
        rating = user["rating_sum"] / user["rating_count"]
    
    text = (
        f"👤 <b>Ваш профиль</b>\n"
        f"⭐ Рейтинг: {rating:.1f} ({user.get('rating_count', 0)} отзывов)\n"
        f"📢 Активных объявлений: {my_ads}\n"
    )
    await message.answer(text, parse_mode="HTML")