from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Главное меню
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Найти учителя"), KeyboardButton(text="➕ Создать анкету")],
            [KeyboardButton(text="👤 Мой профиль")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )

# Категории (используем и при поиске, и при создании)
CATEGORIES = {
    "math": "📐 Математика",
    "languages": "🇬🇧 Языки",
    "it": "💻 IT / Программирование",
    "science": "🔬 Физика/Химия",
    "arts": "🎨 Творчество"
}

def get_categories_keyboard(action_prefix):
    builder = InlineKeyboardBuilder()
    for key, name in CATEGORIES.items():
        # action_prefix будет либо 'create_cat_', либо 'search_cat_'
        builder.button(text=name, callback_data=f"{action_prefix}{key}")
    builder.adjust(1)
    return builder.as_markup()

# Уровни
def get_levels_keyboard():
    builder = InlineKeyboardBuilder()
    levels = [
        ("🐣 Начинающий", "beginner"),
        ("⚡️ Средний", "middle"),
        ("🔥 Продвинутый", "advanced")
    ]
    for name, code in levels:
        builder.button(text=name, callback_data=f"level_{code}")
    builder.adjust(1)
    return builder.as_markup()