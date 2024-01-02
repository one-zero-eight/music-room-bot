from aiogram import Router

from src.middlewares import RegisteredUserMiddleware

router = Router()

router.message.middleware(RegisteredUserMiddleware())

import src.routers.booking.create_booking_routes  # noqa
import src.routers.booking.my_bookings_routes  # noqa
