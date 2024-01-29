from typing import Any, Union, Dict, Optional

from aiogram import Router, types, Bot
from aiogram.filters import Command, Filter
from aiogram.types import BufferedInputFile, TelegramObject, User, BotCommandScopeChat

from src.api import client, ParticipantStatus
from src.constants import admin_commands, bot_commands
from src.filters import RegisteredUserFilter

router = Router()

router.message.filter(RegisteredUserFilter())


class StatusFilter(Filter):
    _status: ParticipantStatus

    def __init__(self, status: Optional[ParticipantStatus] = None):
        self._status = status

    async def __call__(
        self, event: TelegramObject, event_from_user: User
    ) -> Union[bool, Dict[str, Any]]:
        telegram_id = event_from_user.id
        user = await client.get_me(telegram_id=telegram_id)
        if self._status is None:
            return {"status": user["status"]}

        if user["status"] == self._status:
            return True
        return False


@router.message(Command("admin"), StatusFilter())
async def enable_admin_mode(message: types.Message, bot: Bot, status: str):
    if status == ParticipantStatus.LORD:
        text = "You are the Lord of the Music Room! You can use the following commands:"

        for command in admin_commands:
            text += f"\n{command.command} - {command.description}"

        await message.answer(text)
        await bot.set_my_commands(
            bot_commands + admin_commands,
            scope=BotCommandScopeChat(chat_id=message.from_user.id),
        )
    else:
        await bot.set_my_commands(
            bot_commands, scope=BotCommandScopeChat(chat_id=message.from_user.id)
        )


@router.message(Command("export_participants"), StatusFilter(ParticipantStatus.LORD))
async def export_participants(message: types.Message):
    response = await client.export_participants(message.from_user.id)
    if response:
        bytes_, filename = response
        document = BufferedInputFile(bytes_, filename)
        await message.answer_document(
            document, caption="Here is the list of participants."
        )
    else:
        await message.answer("You don't have access to this command.")
