__all__ = ["client", "InNoHassleMusicRoomAPI"]

import datetime
import json
import os
from typing import Any, Optional

import aiohttp


class InNoHassleMusicRoomAPI:
    api_root_path: str

    def __init__(self, api_root_path: str):
        self.api_root_path = api_root_path

    def _create_session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession()

    # async with aiohttp.ClientSession() as session:
    #     url = "http://127.0.0.1:8000/auth/registration"
    #     user_data = await state.get_data()
    #     email = user_data.get("email")
    #     params = {"email": email}
    #     async with session.post(url, params=params) as response:
    #         if response.status == 400:
    #             await callback.message.answer("A user with the provided email is already registered.")
    #         if response.status == 200:
    #             await callback.message.answer("We sent a one-time code on your email. Please, enter it.")
    #             await state.set_state(Registration.code_requested)
    async def start_registration(self, email: str) -> tuple[bool, Any]:
        async with self._create_session() as session:
            url = f"{self.api_root_path}/auth/registration"
            params = {"email": email}
            async with session.post(url, params=params) as response:
                if response.status == 400:
                    return False, "A user with the provided email is already registered."
                if response.status == 200:
                    return True, None

    #
    # url = "http://127.0.0.1:8000/auth/validate_code"
    # params = {"email": email, "code": message.text, "telegram_id": telegram_id}
    # async with aiohttp.ClientSession() as session:
    #     async with session.post(url, params=params) as response:
    #         await response.text()
    #         if response.status == 200:
    #             await message.answer(
    #                 text="Your code has been accepted. To use the music room, you need to fill out your profile."
    #             )
    #             await asyncio.sleep(0.8)
    #             await message.answer(
    #                 text="Please provide access to your phone.",
    #                 reply_markup=phone_request_kb,
    #             )
    #             await state.set_state(Registration.phone_number_requested)
    #         elif response.status == 400:
    #             await message.answer(text="Incorrect code. Please, enter the code again.")
    #             return
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

    async def is_user_exists(self, telegram_id: str) -> bool:
        async with self._create_session() as session:
            url = f"{self.api_root_path}/auth/is_user_exists"
            params = {"telegram_id": telegram_id}
            async with session.get(url, params=params) as response:
                response_text = await response.text()
                user_exists = json.loads(response_text)
                return user_exists

    async def fill_profile(self, name: str, email: str, alias: str, phone_number: str) -> tuple[bool, Any]:
        async with self._create_session() as session:
            url = f"{self.api_root_path}/participants/fill_profile"
            params = {
                "name": name,
                "email": email,
                "alias": alias,
                "phone_number": phone_number,
            }
            async with session.post(url, json=params) as response:
                await response.text()
                if response.status == 200:
                    return True, None
                else:
                    return False, "There was an error during filling profile."

    # async def get_image_schedule_from_api(current_week: datetime.date):
    #     async with aiohttp.ClientSession() as session:
    #         url = "http://127.0.0.1:8000/bookings/form_schedule"
    #         params = {"start_of_week": str(current_week)}
    #
    #         async with session.get(url, params=params) as response:
    #             if response.status == 200:
    #                 image_bytes = await response.read()
    #                 return BufferedInputFile(image_bytes, "schedule.png")
    async def get_image_schedule(self, start_of_week: datetime.date) -> Optional[bytes]:
        async with self._create_session() as session:
            url = f"{self.api_root_path}/bookings/form_schedule"
            params = {"start_of_week": start_of_week.isoformat()}

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    image_bytes = await response.read()
                    return image_bytes

    # async def get_participant_id(telegram_id: int):
    #     url = "http://127.0.0.1:8000/participants/participant_id"
    #     params = {"telegram_id": str(telegram_id)}
    #     async with aiohttp.ClientSession() as session:
    #         async with session.get(url, params=params) as response:
    #             response_text = await response.text()
    #             response_json = json.loads(response_text)
    #             return response_json
    async def get_participant_id(self, telegram_id: int) -> Optional[int]:
        url = f"{self.api_root_path}/participants/participant_id"
        params = {"telegram_id": str(telegram_id)}
        async with self._create_session() as session:
            async with session.get(url, params=params) as response:
                response_text = await response.text()
                response_json = json.loads(response_text)
                return response_json

    # async def run_process_booking_creation(
    #     user_id: str,
    #     date: datetime.date,
    #     time_start: datetime.time,
    #     time_end: datetime.time,
    # ) -> tuple[ClientResponse, json]:
    #     params = {
    #         "participant_id": user_id,
    #         "time_start": datetime.datetime.combine(date, time_start).isoformat(),
    #         "time_end": datetime.datetime.combine(date, time_end).isoformat(),
    #     }
    #     async with aiohttp.ClientSession() as session:
    #         url = "http://127.0.0.1:8000/bookings/"
    #         async with session.post(url, json=params) as response:
    #             response_text = await response.text()
    #             response_json = json.loads(response_text)
    #             return response, response_json
    async def book(
        self, user_id: int, date: datetime.date, time_start: datetime.time, time_end: datetime.time
    ) -> tuple[bool, Any]:
        params = {
            "participant_id": user_id,
            "time_start": datetime.datetime.combine(date, time_start).isoformat(),
            "time_end": datetime.datetime.combine(date, time_end).isoformat(),
        }
        async with self._create_session() as session:
            url = f"{self.api_root_path}/bookings/"
            async with session.post(url, json=params) as response:
                if response.status == 200:
                    return True, None
                else:
                    response_json = await response.json()
                    return False, response_json.get("detail")

    # async def get_daily_bookings():
    #     async with aiohttp.ClientSession() as session:
    #         url = "http://127.0.0.1:8000/bookings/daily_bookings"
    #         params = {"day": datetime.datetime.now().isoformat()}
    #         async with session.get(url, params=params) as response:
    #             response_text = await response.text()
    #             response_json = json.loads(response_text)
    #             return response, response_json
    async def get_daily_bookings(self) -> tuple[bool, Any]:
        async with self._create_session() as session:
            url = f"{self.api_root_path}/bookings/daily_bookings"
            params = {"day": datetime.datetime.now().isoformat()}
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    response_text = await response.text()
                    response_json = json.loads(response_text)
                    return True, response_json
                else:
                    return False, None

    async def get_remaining_daily_hours(self, participant_id: int, date: datetime.date) -> Optional[float]:
        async with self._create_session() as session:
            url = f"{self.api_root_path}/participants/{participant_id}/remaining_daily_hours"
            params = {"date": date.isoformat()}
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return None
                remaining_daily_hours = float(await response.text())
        return remaining_daily_hours


client = InNoHassleMusicRoomAPI(os.getenv("API_ROOT_PATH"))
