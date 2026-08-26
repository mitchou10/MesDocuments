from fastapi import APIRouter

from app.routers.v1.auth import router as auth_router
from app.routers.v1.favorites import router as favorites_router
from app.routers.v1.files import router as files_router
from app.routers.v1.folders import router as folders_router
from app.routers.v1.shares import router as shares_router
from app.routers.v1.users import router as users_router

router = APIRouter(prefix="/api/v1")
router.include_router(auth_router)
router.include_router(folders_router)
router.include_router(files_router)
router.include_router(shares_router)
router.include_router(favorites_router)
router.include_router(users_router)
