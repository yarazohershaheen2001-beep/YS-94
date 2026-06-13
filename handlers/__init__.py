from .start import router as start_router
from .menu import router as menu_router
from .platforms import router as platforms_router
from .payment import router as payment_router
from .admin import router as admin_router

__all__ = [
    "start_router",
    "menu_router",
    "platforms_router",
    "payment_router",
    "admin_router",
]
