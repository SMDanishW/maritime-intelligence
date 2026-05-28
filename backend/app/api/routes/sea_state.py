from fastapi import APIRouter

from app.services.digitraffic import sea_state_service

router = APIRouter()


@router.get("")
async def get_sea_state():
    return await sea_state_service.get_sea_state()
