import logging
import sys
import telebot

from contextlib import _AsyncGeneratorContextManager

from telebot.types import Message, ReplyKeyboardMarkup, InlineKeyboardMarkup
from telebot.states.asyncio.context import StateContext
from telebot.async_telebot import AsyncTeleBot
from telebot.states import State

from sqlalchemy.ext.asyncio import AsyncSession

from config import Config
from packages.botapi.state_controller import StateController
from packages.botmaster import BotMaster


log_dir = Config.GetValue("LOG_DIR")
log_dir = log_dir if log_dir is not None else ""

route_logger = logging.getLogger("BaseBotRoute")
route_logger.setLevel(logging.INFO)

handler = logging.FileHandler(f"{log_dir}BaseBotRoute.log", mode='w')
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

handler.setFormatter(formatter)

route_logger.addHandler(handler)

class BaseBotRoute:

    """Class for creating an API fake route inside Telegram bot."""

    # This is fields that we are recieving in time we called
    __stateControl: StateController
    __usersMessage: Message
    __botmas: BotMaster
    __userId: int
    
    # This fields we passing at creating phase
    __commands: list | tuple = None
    __contentTypes: list | tuple = None
    __regexp: str = None
    __func: object = None
    __statmentState: State | str = None
    __isDigit: bool = None
    __keyboard: ReplyKeyboardMarkup | InlineKeyboardMarkup = None
    __session: _AsyncGeneratorContextManager[AsyncSession]
    __logger: logging.Logger
    
    # Getters
    @property
    def StateControl(self): 
        """StateControl object to controlling User's states. Usually built with Redis database."""
        return self.__stateControl
    
    @property
    def UserMessage(self): 
        """User's last message extracted from callback."""
        return self.__usersMessage
    
    @property
    def Botmas(self): 
        """BotMaster object for controlling Bot's behavior."""
        return self.__botmas
    
    @property
    def Commands(self): 
        """Commands list that will **trigger** this route. Should be strings."""
        return self.__commands
    
    @property
    def ContentTypes(self): 
        """Type list of contents that will **trigger** this route. Should be strings."""
        return self.__contentTypes
    
    @property
    def Regexp(self): 
        """Regular expression that will **trigger** this route. Shoul be string. Except \\ backslashes."""
        return self.__regexp
    
    @property
    def Func(self): 
        """**Lambda** function that can filter incoming messages to choose which will **trigger** the route."""
        return self.__func
    
    @property
    def StatmentState(self): 
        """State from **`telebot.types.State`**. Filter. Decides in which State route can be triggered"""
        return self.__statmentState
    
    @property
    def IsDigit(self): 
        """Filter telling that the route can be triggered only if message contains only digit chars."""
        return self.__isDigit
    
    @property
    def Keyboard(self): 
        """Reply keyboard to pin up with Bot's message. Can be two types **`ReplyKeyboardMarkup`** or **`InlineKeyboardMarkup`**."""
        return self.__keyboard
    
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
    @StateControl.setter
    def StateControl(self, value: StateController): self.__stateControl = value;
    
    @UserMessage.setter
    def UserMessage(self, value: Message): self.__usersMessage = value;
    
    @Botmas.setter
    def Botmas(self, value: BotMaster): self.__botmas = value;
    
    @Commands.setter
    def Commands(self, value: list | tuple): self.__commands = value;
    
    @ContentTypes.setter
    def ContentTypes(self, value: list | tuple): self.__contentTypes = value;
    
    @Regexp.setter
    def Regexp(self, value: str): self.__regexp = value;
    
    @Func.setter
    def Func(self, value: object): self.__func = value;
    
    @StatmentState.setter
    def StatmentState(self, value: State |  str): self.__statmentState = value;
    
    @IsDigit.setter
    def IsDigit(self, value: bool): self.__isDigit = value;
    
    @Keyboard.setter
    def Keyboard(self, value: ReplyKeyboardMarkup |  InlineKeyboardMarkup): self.__keyboard = value;
    
    @UserId.setter
    def UserId(self, value: int): self.__userId = value;
    
    @Session.setter
    def Session(self, value: _AsyncGeneratorContextManager[AsyncSession]): self.__session = value;

    @Log.setter
    def Log(self, value: logging.Logger): self.__logger = value

    def __new__(cls):
        instance = super().__new__(cls)
        
        instance.Log = route_logger
        return instance

    def __init__(self, sess: _AsyncGeneratorContextManager[AsyncSession]) -> None:
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

    async def __call__(self, message: telebot.types.Message, state: StateContext, bot: AsyncTeleBot) -> None:
        
        self.Botmas = BotMaster(bot) # Creating BotMaster object to control the bot
        self.UserMessage = message
        self.StateControl = StateController(state)
        
        # Obvious, extract chat id (user id) 
        # from message if message exist
        if self.UserMessage is not None:
            self.UserId = self.UserMessage.chat.id
        
        