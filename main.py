import telebot
from config import Config

from packages.botapi.bot_api import BotApi

from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateRedisStorage

from packages.database import get_session
from packages.database.models.schemas.User import User
from packages.keyboard import InlineKeyboard
import packages.scenarios
from packages.scenarios.connection import Connection_CB
from packages.scenarios.mainstart import MainStart_API, MainStart_CB

from telebot.types import ReactionTypeEmoji, Message, MessageReactionUpdated, InlineKeyboardButton

from packages.scenarios.making_post import MakePostConfirmedPhoto, MakePostConfirmedPhotoSplit, MakePostConfirmedPostView, MakePostEnterText_CB, MakePostGotPhoto, MakePostGotText, MakePostRetryPhotos, MakePostRetryText, MakePostSkippedPhoto

redis_host = Config.GetValue("REDIS_HOST")
redis_port = Config.GetValue("REDIS_PORT")
redis_pass = Config.GetValue("REDIS_PASS")

redis_store = StateRedisStorage(port=redis_port, host=redis_host, password=redis_pass)

bot = AsyncTeleBot(Config.GetValue("TOKEN"))

@bot.my_chat_member_handler()
async def mmm(message: telebot.types.ChatMemberUpdated):
    old = message.old_chat_member
    new = message.new_chat_member
    
    keyboard = InlineKeyboard()
    keyboard += InlineKeyboardButton("Назад", callback_data="mainmenu")
    
    if new.status == "member":
        await bot.leave_chat(message.chat.id)
    elif new.status == "administrator":
        user_id_who_did_invite = message.from_user.id
        user = await User.get_by_telegram_id(get_session(), user_id_who_did_invite)
        await user.update_chat_id(get_session(), message.chat.id)
        await bot.send_message(message.from_user.id, f"Подключенный канал/группа обновлен.", reply_markup=keyboard.Keyboard)



app = BotApi(bot)

app += MainStart_API()
app *= MainStart_CB()
app *= Connection_CB()
app *= MakePostEnterText_CB()
app += MakePostSkippedPhoto()
app += MakePostGotText()
app += MakePostRetryText()
app += MakePostRetryPhotos()
app += MakePostGotPhoto()
app += MakePostConfirmedPhoto()
app += MakePostConfirmedPhotoSplit()
app += MakePostConfirmedPostView()

# Type down here routes:
# app += ... for regular routes;
# app *= ... for callback routes.

app.Poll()