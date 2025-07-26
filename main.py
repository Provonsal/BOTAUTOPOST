import telebot
from config import Config

from packages.botapi.bot_api import BotApi

from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateRedisStorage

import packages.scenarios
from packages.scenarios.test import MainStart

redis_host = Config.GetValue("REDIS_HOST")
redis_port = Config.GetValue("REDIS_PORT")
redis_pass = Config.GetValue("REDIS_PASS")

redis_store = StateRedisStorage(port=redis_port, host=redis_host, password=redis_pass)

bot = AsyncTeleBot(Config.GetValue("TOKEN"))

@bot.my_chat_member_handler()
async def mmm(message: telebot.types.ChatMemberUpdated):
    old = message.old_chat_member
    new = message.new_chat_member
    if new.status == "member":
        await bot.send_message(message.chat.id, f"{message.from_user.id} {message.from_user.full_name} i invited from as member of a group") # Welcome message, if bot was added to group
    elif new.status == "administrator":
        await bot.send_message(message.chat.id, f"{message.from_user.id} {message.from_user.full_name} i invited from as admin")

app = BotApi(bot)

app += MainStart()

# Type down here routes:
# app += ... for regular routes;
# app *= ... for callback routes.

app.Poll()