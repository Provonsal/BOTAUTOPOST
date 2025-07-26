from io import BufferedReader

import logging
import sys
from typing import Optional

from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio.middleware import StateMiddleware
from telebot import asyncio_filters
from telebot.types import InlineKeyboardMarkup, ReplyKeyboardMarkup

from config import Config
from packages.database import init_db


log_dir = Config.GetValue("LOG_DIR")
log_dir = log_dir if log_dir is not None else ""

botmaster_logger = logging.getLogger("BotMaster")
botmaster_logger.setLevel(logging.INFO)

handler = logging.FileHandler(f"{log_dir}BotMaster.log", mode='w')
console_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

botmaster_logger.addHandler(console_handler)
botmaster_logger.addHandler(handler)

botmaster_logger.debug(f"Logger for class BotMaster successfully created.")

class BotMaster():
    
    __bot: AsyncTeleBot
    __logger: logging.Logger
    
    @property
    def Bot(self): 
        """Async TeleBot object"""
        return self.__bot
    
    @property
    def Log(self):
        return self.__logger
    
    @Bot.setter
    def Bot(self, value: AsyncTeleBot): self.__bot = value;

    @Log.setter
    def Log(self, value: logging.Logger): self.__logger = value;

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)        
        instance.Log = botmaster_logger
        return instance

    def __init__(self, bot: AsyncTeleBot) -> None:
        self.Log.debug("Start initialization of botmaster.")
        self.Bot = bot
        self.Log.debug("Initialization successfully completed.")

    async def Poll(self) -> None:

        """
        Method to start polling updates to bot.  
        
        ---
        
        **Caution!**  
        Can be only one polling active at once.
        """

        # RUS: Инициализируем базу данных для работы с ней.
        # ENG: Initializing database for use.
        self.Log.info("Initializing database models...")
        await init_db()

        # RUS: Включаем что-то, руководство сказало включить это.
        # ENG: Turn on something, just guide told me to do it.
        self.Log.info("Setting up middleware and filters...")
        
        self.Bot.setup_middleware(StateMiddleware(self.Bot))
        
        # RUS: Добавляем кастомные фильтры для цифр и для того чтобы работали "состояния пользователей".
        # ENG: Adding custom filters for digits and for "User states"'s work.
        self.Bot.add_custom_filter(asyncio_filters.StateFilter(self.Bot))
        self.Bot.add_custom_filter(asyncio_filters.IsDigitFilter())

        # RUS: Запускаем поллинг.
        # ENG: Start polling.
        self.Log.info("Starting polling...")
        await self.Bot.infinity_polling()

    async def send_message(self, user_id: int, message: str, reply_markup: Optional[InlineKeyboardMarkup | ReplyKeyboardMarkup] = None) -> None:
        """Send message to user by his id."""
        await self.Bot.send_message(user_id, message, reply_markup=reply_markup)
        self.Log.info(f"Sended message to {user_id}.")
            
    async def edit_message(self, text: str, user_id: int, message_id: int, reply_markup: Optional[InlineKeyboardMarkup] = None) -> None:
        """Edit message **text** and **reply markup** in chat with user and by **message id**."""
        await self.Bot.edit_message_text(text, user_id, message_id, reply_markup=reply_markup)
        self.Log.info(f"Edited message {message_id} in chat with {user_id}.")
        
    async def send_photo(self, user_id: int, photo: BufferedReader, caption: str | None, reply_markup: Optional[InlineKeyboardMarkup | ReplyKeyboardMarkup] = None):
        """Send photo to user by his id. Photo caption is optional."""
        await self.Bot.send_photo(user_id, photo, caption, reply_markup=reply_markup)
        self.Log.info(f"Sended photo to {user_id}.")
