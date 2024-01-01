import datetime

from aiogram import F, Router, types
from aiogram.types import BufferedInputFile

from src.api import client
from src.keyboards import ImageScheduleCallbackData, image_schedule_kb

router = Router()


@router.message(F.text == "Show the image with bookings")
async def get_image_schedule(message: types.Message):
    await message.answer(
        text="Do you want to see bookings for the current week or next one?",
        reply_markup=image_schedule_kb,
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
    start_of_week = get_start_of_week(choice == "schedule:current_week")
    image_bytes = await client.get_image_schedule(start_of_week)
    photo = BufferedInputFile(image_bytes, "schedule.png")
    if choice == "schedule:current_week":
        await callback.message.answer("Sending image for the current week...")
    else:
        await callback.message.answer("Sending image for the next week...")
    await callback.bot.send_photo(chat_id=chat_id, photo=photo)
