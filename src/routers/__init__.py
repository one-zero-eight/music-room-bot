from src.routers.booking import router as router_bookings
from src.routers.registration import router as router_registration
from src.routers.schedule import router as router_image_schedule
from src.routers.admin import router as router_admin

routers = [
    router_bookings,
    router_registration,
    router_image_schedule,
    router_admin,
]
