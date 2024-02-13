__all__ = ["client", "InNoHassleMusicRoomAPI", "ParticipantStatus"]

import datetime
import json
import os
from enum import StrEnum
from typing import Any, Optional

import aiohttp
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

_BOT_TOKEN = os.getenv("TOKEN")


class ParticipantStatus(StrEnum):
    FREE = "free"
    MIDDLE = "middle"
    SENIOR = "senior"
    LORD = "lord"


class InNoHassleMusicRoomAPI:
    api_root_path: str

    def __init__(self, api_root_path: str):
        self.api_root_path = api_root_path

    def _create_session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession()

    def _auth_session(self, session: aiohttp.ClientSession, telegram_id: int) -> None:
        session.headers.update({"Authorization": f"Bearer {telegram_id}:{_BOT_TOKEN}"})

    async def start_registration(self, email: str) -> tuple[bool, Any]:
        async with self._create_session() as session:
            url = f"{self.api_root_path}/auth/registration"
            params = {"email": email}
            async with session.post(url, params=params) as response:
                if response.status == 400:
                    return (
                        False,
                        "A user with the provided email is already registered.",
                    )
                if response.status == 200:
                    return True, None

    async def validate_code(self, email: str, code: str, telegram_id: str) -> tuple[bool, Any]:
        async with self._create_session() as session:
            url = f"{self.api_root_path}/auth/validate_code"
            params = {"email": email, "code": code, "telegram_id": telegram_id}
            async with session.post(url, params=params) as response:
                await response.text()
                if response.status == 200:
                    return True, None
                elif response.status == 400:
                    return False, "Incorrect code. Please, enter the code again."

    async def is_user_exists(self, telegram_id: int) -> bool:
        async with self._create_session() as session:
            url = f"{self.api_root_path}/auth/is_user_exists"
            params = {"telegram_id": str(telegram_id)}
            async with session.get(url, params=params) as response:
                response_text = await response.text()
                user_exists = json.loads(response_text)
                return user_exists

    async def is_need_to_fill_profile(self, telegram_id: int) -> bool | None:
        async with self._create_session() as session:
            url = f"{self.api_root_path}/auth/is_need_to_fill_profile"
            params = {"telegram_id": str(telegram_id)}
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return None
                response_text = await response.text()
                need_to_fill_profile = json.loads(response_text)
                return need_to_fill_profile

    async def get_participant_id(self, telegram_id: int) -> Optional[int]:
        url = f"{self.api_root_path}/participants/participant_id"
        params = {"telegram_id": str(telegram_id)}
        async with self._create_session() as session:
            async with session.get(url, params=params) as response:
                response_text = await response.text()
                response_json = json.loads(response_text)
                return response_json

    async def get_me(self, telegram_id: int) -> Optional[dict]:
        url = f"{self.api_root_path}/participants/me"
        async with self._create_session() as session:
            self._auth_session(session, telegram_id)
            async with session.get(url) as response:
                response_text = await response.text()
                response_json = json.loads(response_text)
                if response.status == 200:
                    return response_json

    async def fill_profile(self, telegram_id: int, name: str, alias: str, phone_number: str) -> tuple[bool, Any]:
        url = f"{self.api_root_path}/participants/me/fill_profile"
        body = {
            "name": name,
            "alias": alias,
            "phone_number": phone_number,
        }
        async with self._create_session() as session:
            self._auth_session(session, telegram_id)

            async with session.post(url, json=body) as response:
                await response.text()
                if response.status == 200:
                    return True, None
                else:
                    return False, "There was an error during filling profile."

    async def get_remaining_daily_hours(
        self,
        telegram_id: int,
        date: str,
    ) -> Optional[float]:
        url = f"{self.api_root_path}/participants/me/remaining_daily_hours"
        params = {"date": date}

        async with self._create_session() as session:
            self._auth_session(session, telegram_id)
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return None
                remaining_daily_hours = float(await response.text())
        return remaining_daily_hours

    async def get_daily_bookings(self, date: Optional[str]) -> tuple[bool, Any]:
        async with self._create_session() as session:
            url = f"{self.api_root_path}/bookings/daily_bookings"
            params = {"date": date if date else datetime.date.today().isoformat()}
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    response_text = await response.text()
                    response_json = json.loads(response_text)
                    return True, response_json
                else:
                    return False, None

    async def book(
        self,
        telegram_id: int,
        date: datetime.date,
        time_start: datetime.time,
        time_end: datetime.time,
    ) -> tuple[bool, Any]:
        url = f"{self.api_root_path}/bookings/"
        params = {
            "time_start": datetime.datetime.combine(date, time_start).isoformat(),
            "time_end": datetime.datetime.combine(date, time_end).isoformat(),
        }

        async with self._create_session() as session:
            self._auth_session(session, telegram_id)
            async with session.post(url, json=params) as response:
                if response.status == 200:
                    return True, None
                else:
                    response_json = await response.json()
                    return False, response_json.get("detail")

    async def get_participant_bookings(self, telegram_id: int) -> Optional[list[dict]]:
        url = f"{self.api_root_path}/bookings/my_bookings"

        async with aiohttp.ClientSession() as session:
            self._auth_session(session, telegram_id)
            async with session.get(url) as response:
                response_text = await response.text()
                response_json = json.loads(response_text)
                if response.status == 200:
                    return response_json

    async def delete_booking(self, booking_id: int, telegram_id: int) -> bool:
        url = f"{self.api_root_path}/bookings/{booking_id}"
        params = {"booking_id": booking_id}

        async with self._create_session() as session:
            self._auth_session(session, telegram_id)
            async with session.delete(url, params=params) as response:
                return True if response.status == 200 else False

    async def get_image_schedule(self, start_of_week: datetime.date) -> Optional[bytes]:
        url = f"{self.api_root_path}/bookings/form_schedule"
        params = {"start_of_week": start_of_week.isoformat()}

        async with self._create_session() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.read()

    async def export_participants(self, telegram_id: int) -> tuple[bytes, str]:
        url = f"{self.api_root_path}/participants/export"

        async with self._create_session() as session:
            self._auth_session(session, telegram_id=telegram_id)
            async with session.get(url) as response:
                if response.status == 200:
                    bytes_ = await response.read()
                    filename = response.headers["Content-Disposition"].split("filename=")[1]
                    return bytes_, filename


load_dotenv(find_dotenv())

client: InNoHassleMusicRoomAPI = InNoHassleMusicRoomAPI(os.getenv("API_ROOT_PATH"))
