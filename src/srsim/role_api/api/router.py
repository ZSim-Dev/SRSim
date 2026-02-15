from fastapi import APIRouter

from srsim.role_api.api.role import router as role_router

router = APIRouter()
router.include_router(role_router)
