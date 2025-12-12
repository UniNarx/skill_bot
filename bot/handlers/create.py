from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from bot.states import CreateAdFSM
from bot.keyboards import get_categories_keyboard, get_levels_keyboard, get_main_keyboard, CATEGORIES
from database.mongo import ads_collection
from datetime import datetime

router = Router()

@router.message(F.text == "➕ Создать анкету")
async def start_create(message: types.Message, state: FSMContext):
    if not message.from_user.username:
        return await message.answer("❌ Ошибка: У вас нет Username. Установите его в настройках Telegram, чтобы создать анкету.")
    
    await message.answer("Выберите категорию, в которой хотите обучать:", reply_markup=get_categories_keyboard("create_cat_"))
    await state.set_state(CreateAdFSM.choosing_category)

@router.callback_query(F.data.startswith("create_cat_"))
async def category_chosen(callback: types.CallbackQuery, state: FSMContext):
    cat_key = callback.data.split("_")[2]
    cat_name = CATEGORIES.get(cat_key, "Другое")
    
    await state.update_data(category=cat_key, category_name=cat_name)
    await callback.message.edit_text(f"Категория: <b>{cat_name}</b>\nТеперь выберите ваш уровень владения:", 
                                     reply_markup=get_levels_keyboard(), parse_mode="HTML")
    await state.set_state(CreateAdFSM.choosing_level)

@router.callback_query(F.data.startswith("level_"))
async def level_chosen(callback: types.CallbackQuery, state: FSMContext):
    level = callback.data.split("_")[1]
    await state.update_data(level=level)
    
    await callback.message.edit_text("✍️ Напишите краткое описание (до 140 символов).\nНапример: <i>Помогаю с ЕГЭ, объясняю интегралы.</i>", parse_mode="HTML")
    await state.set_state(CreateAdFSM.writing_desc)

@router.message(CreateAdFSM.writing_desc)
async def finish_create(message: types.Message, state: FSMContext):
    description = message.text[:140] # Обрезаем если длинно
    data = await state.get_data()
    user = message.from_user
    
    # Удаляем старое объявление в этой же категории (чтобы не дублировать)
    await ads_collection.delete_many({"author_id": user.id, "category": data['category']})
    
    new_ad = {
        "author_id": user.id,
        "username": user.username,
        "category": data['category'],
        "level": data['level'],
        "description": description,
        "is_active": True,
        "date_created": datetime.now()
    }
    
    await ads_collection.insert_one(new_ad)
    await message.answer(f"✅ <b>Анкета создана!</b>\n\nКатегория: {data['category_name']}\nОписание: {description}", 
                         reply_markup=get_main_keyboard(), parse_mode="HTML")
    await state.clear()