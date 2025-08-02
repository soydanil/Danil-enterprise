from fastapi import APIRouter

from src.api.v1.endpoints import router as v1_router

router = APIRouter(prefix="/api/v1")
router.include_router(v1_router)
