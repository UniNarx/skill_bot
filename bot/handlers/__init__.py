from aiogram import Router
from .common import router as common_router
from .create import router as create_router
from .search import router as search_router

router = Router()

router.include_router(common_router)
router.include_router(create_router)
router.include_router(search_router)