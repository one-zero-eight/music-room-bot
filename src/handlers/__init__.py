from src.handlers.create_booking import router as router_bookings
from src.handlers.registration import router as router_registration
from src.handlers.schedule import router as router_image_schedule

routers = [router_registration, router_image_schedule, router_bookings]
