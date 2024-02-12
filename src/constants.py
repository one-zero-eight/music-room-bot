from aiogram import types

instructions_url = "https://bit.ly/inno-music-room"
how_to_get_url = "https://www.youtube.com/watch?v=mGfdun8ah3g"
tg_chat_url = "https://t.me/joinchat/DjhyZkBN-FmZStxTB40qwQ"
bot_name = "Music Room Bot"
bot_description = "Book a music room in the Innopolis Sport Complex. Made by @one_zero_eight"
bot_short_description = "Book a music room in the Innopolis Sport Complex. Made by @one_zero_eight"
bot_commands = [
    types.BotCommand(command="/start", description="Start the bot (register)"),
    types.BotCommand(command="/menu", description="Open the menu"),
    types.BotCommand(command="/help", description="Get help"),
    types.BotCommand(command="/create_booking", description="Create a booking"),
    types.BotCommand(command="/my_bookings", description="Show your bookings"),
    types.BotCommand(command="/image_schedule", description="Show the image with bookings"),
    types.BotCommand(command="/refill_profile", description="Refill your profile (name and phone number)"),
]
admin_commands = [
    types.BotCommand(command="/admin", description="Enable admin mode"),
    types.BotCommand(command="/export_participants", description="Export participants in docx format"),
]

rules_message = (
    "After you have crossed the threshold of the room, you must follow the rules described below. In case of "
    "non-compliance, you would be permanently banned from the music room and all corresponding resources.\n\n"
    "🚫 Do not remove property from the room.\n"
    "🚫 Do not bring any food and/or drinks into the room. In case you really need to eat or drink, you can do it "
    "outside the room.\n"
    "🚫 Don't leave trash in the room. There is no trash bin in the room, the nearest one is located right at the "
    "entrance of the sports complex.\n"
    "🚫 Do not fix instruments if they are broken (including broken strings on guitars). It's better to report this "
    "in the chat so that the technician can repair them in the future.\n"
    "⚠️ If you don't know how to tune the instrument, don't do it yourself. Find someone who knows and ask him/her "
    "to teach or help you with it.\n"
    "⚠️ Unnecessarily, do not move the equipment.\n"
)
rules_confirmation_message = """I agree to and will abide by the stated rules."""
