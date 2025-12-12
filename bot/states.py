from aiogram.fsm.state import State, StatesGroup

class CreateAdFSM(StatesGroup):
    choosing_category = State()
    choosing_level = State()
    writing_desc = State()