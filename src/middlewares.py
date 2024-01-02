from typing import Callable, Dict, Any, Awaitable, ClassVar

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message

from src.api import client


class RegisteredUserMiddleware(BaseMiddleware):
    """
    Middleware for checking if user is registered
    """

    _cache: ClassVar[Dict[str, bool]] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        # only for user events

        telegram_id = str(event.from_user.id)

        if telegram_id in self._cache:
            api_user_id = self._cache[telegram_id]
        elif await client.is_user_exists(telegram_id):
            api_user_id = await client.get_participant_id(telegram_id)
            self._cache[telegram_id] = api_user_id
        else:
            await event.answer("Welcome! To continue, you need to register. Use /start command.")
            return
        data["api_user_id"] = api_user_id
        return await handler(event, data)
