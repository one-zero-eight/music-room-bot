import datetime

import aiohttp
from aiogram import F, Router, types

from aiogram.types import BufferedInputFile

from src.keyboards import ImageScheduleCallbackData, image_schedule_kb

router = Router()


@router.message(F.text == "Show the image with bookings")
async def get_image_schedule(message: types.Message):
    await message.answer(
        text="Do you want to see bookings for the current week or next one?", reply_markup=image_schedule_kb
    )


def get_start_of_week(current_week=True):
    today = datetime.date.today()

    if not current_week:
        today += datetime.timedelta(days=7)

    days_until_monday = today.weekday() - 0

    start_of_week = today - datetime.timedelta(days=days_until_monday)

    return start_of_week


@router.callback_query(ImageScheduleCallbackData.filter(F.key))
async def get_image_schedule_for_current_week(callback: types.CallbackQuery):
    await callback.answer()
    choice = callback.data
    chat_id = callback.from_user.id
    if choice == "schedule:current_week":
        await callback.message.answer("Sending image for the current week...")

        photo = await get_image_schedule_from_api(get_start_of_week(True))
    else:
        await callback.message.answer("Sending image for the next week...")
        photo = await get_image_schedule_from_api(get_start_of_week(False))
    await callback.bot.send_photo(chat_id=chat_id, photo=photo)


async def get_image_schedule_from_api(current_week: datetime.date):
    async with aiohttp.ClientSession() as session:
        url = "http://127.0.0.1:8000/bookings/form_schedule"
        params = {"start_of_week": str(current_week)}

        async with session.get(url, params=params) as response:
            if response.status == 200:
                image_bytes = await response.read()
                return BufferedInputFile(image_bytes, "schedule.png")
