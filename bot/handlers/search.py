from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.mongo import ads_collection, users_collection, connections_collection
from bot.keyboards import get_categories_keyboard, CATEGORIES
from datetime import datetime

router = Router()

@router.message(F.text == "🔍 Найти учителя")
async def start_search(message: types.Message):
    await message.answer("В какой категории ищем учителя?", reply_markup=get_categories_keyboard("search_cat_"))

@router.callback_query(F.data.startswith("search_cat_"))
async def show_ads(callback: types.CallbackQuery):
    cat_key = callback.data.split("_")[2]
    cat_name = CATEGORIES.get(cat_key, "Категория")
    
    # Ищем объявления (лимит 10 самых свежих)
    ads = await ads_collection.find({"category": cat_key, "is_active": True}).sort("date_created", -1).limit(10).to_list(10)
    
    if not ads:
        return await callback.message.edit_text(f"😔 В категории <b>{cat_name}</b> пока нет учителей.", parse_mode="HTML")
    
    # Удаляем старое сообщение с категориями
    await callback.message.delete()
    
    await callback.message.answer(f"🔎 Учителя в категории: <b>{cat_name}</b>", parse_mode="HTML")
    
    for ad in ads:
        # Получаем рейтинг автора
        author = await users_collection.find_one({"user_id": ad['author_id']})
        rating_val = 0.0
        if author and author.get("rating_count", 0) > 0:
            rating_val = author["rating_sum"] / author["rating_count"]
            
        level_icon = {"beginner": "🐣", "middle": "⚡️", "advanced": "🔥"}.get(ad['level'], "")
        
        text = (
            f"{level_icon} <b>Уровень: {ad['level'].upper()}</b>\n"
            f"📝 {ad['description']}\n"
            f"⭐ Рейтинг: {rating_val:.1f} ({author.get('rating_count', 0) if author else 0})\n"
        )
        
        # Кнопка связи
        kb = InlineKeyboardBuilder()
        kb.button(text="📞 Связаться / Записаться", callback_data=f"connect_{ad['_id']}")
        
        await callback.message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")

@router.callback_query(F.data.startswith("connect_"))
async def connect_teacher(callback: types.CallbackQuery, bot):
    from bson.objectid import ObjectId
    
    ad_id = callback.data.split("_")[1]
    ad = await ads_collection.find_one({"_id": ObjectId(ad_id)})
    
    if not ad:
        return await callback.answer("Объявление больше не актуально.", show_alert=True)
    
    student_user = callback.from_user

    # 👇 ДОБАВЛЯЕМ ВОТ ЭТУ ПРОВЕРКУ
    if student_user.id == ad['author_id']:
        return await callback.answer("Это ваше собственное объявление! 😅", show_alert=True)
    
    # 1. Записываем коннект в базу (для будущих отзывов)
    await connections_collection.insert_one({
        "student_id": student_user.id,
        "teacher_id": ad['author_id'],
        "ad_id": ObjectId(ad_id),
        "status": "pending",
        "date": datetime.now()
    })
    
    # 2. Выдаем контакт студенту
    teacher_username = ad['username']
    text_student = (
        f"✅ <b>Контакт учителя:</b> @{teacher_username}\n\n"
        f"Напишите ему в личные сообщения: <i>'Привет! Я нашел тебя через бота, хочу заниматься.'</i>\n\n"
        f"⚠️ <b>Просьба:</b> После занятия вернитесь сюда, чтобы оценить учителя!"
    )
    await callback.answer() # Закрываем часики загрузки
    await callback.message.answer(text_student, parse_mode="HTML")
    
    # 3. (Опционально) Уведомляем учителя
    try:
        await bot.send_message(
            ad['author_id'],
            f"👋 <b>Новый ученик!</b>\nПользователь {student_user.full_name} (@{student_user.username}) взял ваш контакт.",
            parse_mode="HTML"
        )
    except:
        pass # Учитель мог заблокировать бота