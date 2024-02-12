from typing import Dict, Any, ClassVar, Union

from aiogram.filters import Filter
from aiogram.types import User, TelegramObject

from src.api import client


class RegisteredUserFilter(Filter):
    _cache: ClassVar[Dict[int, int]] = {}

    async def __call__(self, event: TelegramObject, event_from_user: User) -> Union[bool, Dict[str, Any]]:
        telegram_id = event_from_user.id

        if telegram_id in self._cache:
            api_user_id = self._cache[telegram_id]
        elif await client.is_user_exists(telegram_id):
            api_user_id = await client.get_participant_id(telegram_id)
            self._cache[telegram_id] = api_user_id
        else:
            return False
        return {"api_user_id": api_user_id}


class FilledProfileFilter(Filter):
    _cache: ClassVar[Dict[int, bool]] = {}

    async def __call__(self, event: TelegramObject, event_from_user: User) -> bool:
        telegram_id = event_from_user.id

        if telegram_id in self._cache:
            filled_profile = self._cache[telegram_id]
            if filled_profile:
                return True

        need_to_fill_profile = await client.is_need_to_fill_profile(telegram_id)
        filled_profile = not need_to_fill_profile
        self._cache[telegram_id] = filled_profile
        return filled_profile
