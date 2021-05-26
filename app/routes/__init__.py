from fastapi import APIRouter
from app.routes import item_router, auth_router

router = APIRouter()
router.include_router(item_router.router)
router.include_router(auth_router.router)