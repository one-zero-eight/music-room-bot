from aiogram import Router

from src.filters import RegisteredUserFilter

router = Router()

router.message.filter(RegisteredUserFilter())

import src.routers.booking.create_booking_routes  # noqa
import src.routers.booking.my_bookings_routes  # noqa
