import base64

import aiohttp
from aiogram import F, Router, types
from aiogram.types import BufferedInputFile

router = Router()


@router.message(F.text == "Show the image with bookings")
async def user_want_to_register(message: types.Message):
    await message.answer(text="Sending image...")
    async with aiohttp.ClientSession() as session:
        url = "http://127.0.0.1:8000/bookings/form_schedule"
        async with session.get(url) as response:
            if response.status == 200:
                image_data = await response.text()
                byte_data = base64.b64decode(image_data)
                photo = BufferedInputFile(byte_data, "schedule.jpg")
                await message.answer_photo(photo=photo, caption="Here's the image!")
            else:
                await message.answer(text="Failed to retrieve the image.")
