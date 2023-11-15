from aiogram import Router

from .menu import router as menu_router
from .post import router as post_router
from .publish import router as publish_router


router = Router()
router.include_router(menu_router)
router.include_router(post_router)
router.include_router(publish_router)
