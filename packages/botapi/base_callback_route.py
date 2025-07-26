from contextlib import _AsyncGeneratorContextManager
import sys
from typing import Any, Callable, Optional

from telebot.states.asyncio.context import StateContext
from telebot.async_telebot import AsyncTeleBot
from telebot.types import (Message,
                           ReplyKeyboardMarkup,
                           InlineKeyboardMarkup,
                           CallbackQuery)

from config import Config
from packages.botapi.state_controller import StateController
from packages.botmaster import BotMaster
from sqlalchemy.ext.asyncio import AsyncSession
import logging


log_dir = Config.GetValue("LOG_DIR")
log_dir = log_dir if log_dir is not None else ""

callback_route_logger = logging.getLogger("BaseCallbackApiRoute")
callback_route_logger.setLevel(logging.INFO)

handler = logging.FileHandler(f"{log_dir}BaseCallbackApiRoute.log", mode='w')
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

handler.setFormatter(formatter)

callback_route_logger.addHandler(handler)

class BaseCallbackApiRoute:

    """Class for creating an API callback fake route inside Telegram bot."""

    # This is fields that we are recieving in time we called
    __callback: CallbackQuery
    __userMessage: Message
    __botmas: BotMaster
    __stateControl: StateController
    __userId: int

    # This fields we passing at creating phase
    __func: Optional[Callable]
    __keyboard: ReplyKeyboardMarkup | InlineKeyboardMarkup
    __session: _AsyncGeneratorContextManager[AsyncSession]
    __logger: logging.Logger

    # Getters
    @property
    def Callback(self):
        """Callback recieved in real time during the callback handling."""
        return self.__callback

    @property
    def UserMessage(self):
        """User's last message extracted from callback."""
        return self.__userMessage

    @property
    def Botmas(self):
        """BotMaster object for controlling Bot's behavior."""
        return self.__botmas

    @property
    def Func(self):
        """Lambda function to filter receiving callbacks"""
        return self.__func

    @property
    def Keyboard(self) -> ReplyKeyboardMarkup | InlineKeyboardMarkup | None:
        """Reply keyboard to pin up with Bot's message. Can be two types **`ReplyKeyboardMarkup`** or **`InlineKeyboardMarkup`**."""
        return self.__keyboard

    @property
    def StateControl(self):
        """StateControl object to controlling User's states. Usually built with Redis database."""
        return self.__stateControl

    @property
    def UserId(self):
        """User's **Telegram ID** extracted from recieved callback."""
        return self.__userId

    @property
    def Session(self):
        """Property for getting async session of database. Use with `async with`"""
        return self.__session()
    
    @property
    def Log(self):
        """"""
        return self.__logger

    # Setters
    @Callback.setter
    def Callback(self, value: CallbackQuery): self.__callback = value

    @UserMessage.setter
    def UserMessage(self, value: Message): self.__userMessage = value

    @Botmas.setter
    def Botmas(self, value: BotMaster): self.__botmas = value

    @Func.setter
    def Func(self, value: Optional[Callable]): self.__func = value

    @Keyboard.setter
    def Keyboard(self, value: ReplyKeyboardMarkup | InlineKeyboardMarkup): self.__keyboard = value

    @StateControl.setter
    def StateControl(self, value: StateController): self.__stateControl = value

    @UserId.setter
    def UserId(self, value: str): self.__userId = value

    @Session.setter
    def Session(self, value: _AsyncGeneratorContextManager[AsyncSession]): self.__session = value

    @Log.setter
    def Log(self, value: logging.Logger): self.__logger = value

    def __new__(cls):
        instance = super().__new__(cls)
        
        instance.Log = callback_route_logger
        return instance

    def __init__(self, sess: _AsyncGeneratorContextManager[AsyncSession]):
        """This method is called to initialize the callback for the API. Not implemented"""
        
        self.Log.debug("Start initialization of base api route.")
        
        self.Session = sess
        
        self.Log.debug("Initialization successfully completed.")

    def __init_subclass__(cls):
        
        log_dir = Config.GetValue("LOG_DIR")
        log_dir = log_dir if log_dir is not None else ""
        
        route_logger = logging.getLogger(cls.__name__)
        route_logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(f"{log_dir}{cls.__name__}.log", mode='w')
        console_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
        
        handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        route_logger.addHandler(console_handler)
        route_logger.addHandler(handler)
        
        route_logger.debug(f"Custom logger for class {cls.__name__} successfully created.")
        
        cls.__logger = route_logger

    async def __call__(self, callback: CallbackQuery, state: StateContext, bot: AsyncTeleBot) -> Any:
        self.Callback = callback
        self.StateControl = StateController(state)
        self.Botmas = BotMaster(bot)
        self.UserMessage = self.Callback.message
        self.UserId = self.UserMessage.chat.id
