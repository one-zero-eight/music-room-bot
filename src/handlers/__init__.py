from src.handlers.menu import router as router_menu
from src.handlers.create_booking import router as router_create_bookings
from src.handlers.registration import router as router_registration
from src.handlers.schedule import router as router_image_schedule
from src.handlers.my_bookings import router as router_bookings

routers = [
    router_menu,
    router_create_bookings,
    router_registration,
    router_image_schedule,
    router_bookings,
]
