from aiogram import Router

from src.filters import FilledProfileFilter

router = Router()

router.message.filter(FilledProfileFilter())

import src.routers.booking.create_booking_routes  # noqa
import src.routers.booking.my_bookings_routes  # noqa
