import asyncio
import logging
import sys

from config import Config

from telebot.async_telebot import AsyncTeleBot

from typing import Iterable, overload
from typing_extensions import Self

from packages.botapi.base_callback_route import BaseCallbackApiRoute
from packages.botapi.base_route import BaseBotRoute
from packages.botmaster import BotMaster

log_dir = Config.GetValue("LOG_DIR")
log_dir = log_dir if log_dir is not None else ""

route_logger = logging.getLogger("BotApi")
route_logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
handler = logging.FileHandler(f"{log_dir}BotApi.log", mode='w')
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

console_handler.setFormatter(formatter)
handler.setFormatter(formatter)

route_logger.addHandler(console_handler)
route_logger.addHandler(handler)

route_logger.info(f"Logger for class BotApi successfully created.")

class BotApi:
    
    __handlers: list
    __botmaster: BotMaster
    __logger: logging.Logger
    
    @property
    def Botmas(self): 
        return self.__botmaster
    
    @property
    def Log(self):
        return self.__logger
    
    @Botmas.setter
    def Botmas(self, v: BotMaster): 
        self.__botmaster = v
        
    @Log.setter
    def Log(self, value: logging.Logger):
        self.__logger = value
    
    @overload
    def __iadd__(self, handler: BaseBotRoute) -> Self: ...
        
    @overload
    def __iadd__(self, handler: Iterable[BaseBotRoute]) -> Self: ...
    
    def __iadd__(self, handler):
        
        if isinstance(handler, Iterable):
            
            for i in handler:
                if isinstance(i, BaseBotRoute):
                    self.AddHandler(i)
                    self.__handlers.append(i)
                else:
                    self.Log.error(f"Object inside iterable are not correct. Got {i.__class__.__name__} type but expected {BaseBotRoute.__name__}.")
                    raise TypeError()
        elif isinstance(handler, BaseBotRoute):
            self.AddHandler(handler)
            self.__handlers.append(handler)
        else:
            self.Log.error("Handler does not have correct type and not recognized.")
            raise TypeError()
        return self
    
    @overload
    def __imul__(self, handler: BaseCallbackApiRoute) -> Self: ...
        
    @overload
    def __imul__(self, handler: Iterable[BaseCallbackApiRoute]) -> Self: ...
    
    def __imul__(self, handler):
        
        if isinstance(handler, Iterable):
            
            for i in handler:
                if isinstance(i, BaseCallbackApiRoute):
                    self.AddCallBackHandler(i)
                    self.__handlers.append(i)
                else:
                    self.Log.error(f"Object inside iterable are not correct. Got {i.__class__.__name__} type but expected {BaseCallbackApiRoute.__name__}.")
                    raise TypeError()
        elif isinstance(handler, BaseCallbackApiRoute):
            self.AddCallBackHandler(handler)
            self.__handlers.append(handler)
        else:
            self.Log.error("Handler does not have correct type and not recognized.")
            raise TypeError()
        return self
    
    def Poll(self) -> None:
        if len(self.__handlers) == 0:
            self.Log.warning("Handlers list are empty. Didn't you add any handlers to the bot?")
        else:
            msg = "Starting polling process with these handlers:\n"
            
            for handler in self.__handlers:
                msg += " - "+handler.__class__.__name__+"\n"
            
            if msg[-1] == "\n":
                msg = msg[:-1]
            
            self.Log.info(msg)
        
        async_debug = Config.GetValue("ASYNC_DEBUG")
        
        if async_debug is None:
            self.Log.warning("Async mode are not setted. Switching to the default mode (no debug).")
            async_debug = False
        elif len(async_debug) == 0:
            self.Log.error("Empty string cant be interpreted. Switching to the default mode (no debug).", exc_info=True)
            async_debug = False
        else:
            try:
                async_debug = bool(int(async_debug))
            except ValueError:
                self.Log.error("Can't transform string to integer. Due to the unrecognizable value switching to the default mode (no debug).", exc_info=True)
                async_debug = False
                
        self.Log.info(f"Async debug mode setted to {async_debug}.")
        
        asyncio.run(self.Botmas.Poll(), debug=async_debug)
        
    def AddHandler(self, handler: BaseBotRoute) -> None:
        self.Botmas.Bot.register_message_handler(
            handler, # type: ignore
            handler.ContentTypes,
            handler.Commands,
            handler.Regexp,
            handler.Func,
            is_digit=handler.IsDigit,
            pass_bot=True
        )
        self.Log.info(f"Added a new handler {handler.__class__.__name__}.")
        
    def AddCallBackHandler(self, handler: BaseCallbackApiRoute):
        self.Botmas.Bot.register_callback_query_handler(
            handler, # type: ignore
            handler.Func,
            pass_bot=True
        )
        self.Log.info(f"Added a new callback handler {handler.__class__.__name__}.")
    
    def AddMyChatMemberHandler(self, handler):
        self.Botmas.Bot.register_my_chat_member_handler(handler, handler.Func, pass_bot=True)
        
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        
        instance.Log = route_logger
        return instance
        
    def __init__(self, bot: AsyncTeleBot, botmas: BotMaster | None = None) -> None:
        self.Log.debug("Start initialization of bot api.")
        
        self.Botmas = botmas if botmas is not None else BotMaster(bot)
        self.__handlers = []
        
        self.Log.debug("Initialization successfully completed.")