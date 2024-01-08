from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import BufferedInputFile

from src.api import client
from src.middlewares import RegisteredUserMiddleware

router = Router()
router.message.middleware(RegisteredUserMiddleware())


@router.message(Command("export_participants"))
async def export_participants(message: types.Message):
    response = await client.export_participants(message.from_user.id)
    if response:
        bytes_, filename = response
        document = BufferedInputFile(bytes_, filename)
        await message.answer_document(document, caption="Here is the list of participants.")
    else:
        await message.answer("You don't have access to this command.")
