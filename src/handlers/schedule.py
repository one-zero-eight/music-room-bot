import base64

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


@router.callback_query(ImageScheduleCallbackData.filter(F.key))
async def get_image_schedule_for_current_week(callback: types.CallbackQuery):
    await callback.answer()
    choice = callback.data
    chat_id = callback.from_user.id
    if choice == "schedule:current_week":
        await callback.bot.send_message(text="Sending image for the current week...", chat_id=chat_id)
        photo = await get_image_schedule_from_api(True)
    else:
        await callback.bot.send_message(text="Sending image for the next week...", chat_id=chat_id)
        photo = await get_image_schedule_from_api(False)
    await callback.bot.send_photo(chat_id=chat_id, photo=photo)


async def get_image_schedule_from_api(current_week: bool):
    async with aiohttp.ClientSession() as session:
        url = "http://127.0.0.1:8000/bookings/form_schedule"
        params = {"current_week": str(current_week)}
        async with session.get(url, params=params) as response:
            image_data = await response.text()
            byte_data = base64.b64decode(image_data)
            return BufferedInputFile(byte_data, "schedule.jpg")
