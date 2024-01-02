from aiogram import Router

router = Router()

import src.routers.booking.create_booking_routes  # noqa
import src.routers.booking.my_bookings_routes  # noqa
