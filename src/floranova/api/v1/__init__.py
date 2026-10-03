from fastapi import APIRouter
from floranova.api.v1.auth import router as auth_router
from floranova.api.v1.catalog import router as catalog_router
from floranova.api.v1.slots import router as slots_router
from floranova.api.v1.orders import router as orders_router
from floranova.api.v1.inventory import router as inventory_router
from floranova.api.v1.admin_stats import router as admin_stats_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(catalog_router)
api_router.include_router(slots_router)
api_router.include_router(orders_router)
api_router.include_router(inventory_router)
api_router.include_router(admin_stats_router)
