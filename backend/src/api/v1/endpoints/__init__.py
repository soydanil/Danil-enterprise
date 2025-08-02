from fastapi import APIRouter

from .health import router as health_router
from .webhook import router as webhook

router = APIRouter()

# Marked for removal
router.include_router(health_router, tags=["Health"])
router.include_router(webhook, tags=["whatspapp webhook"])


