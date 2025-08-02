import logging

from fastapi import APIRouter, status

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": status.HTTP_200_OK}