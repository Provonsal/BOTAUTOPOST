import logging
import sys
from typing import Union
from telebot.states import State

from telebot.states import asyncio, sync

from config import Config

log_dir = Config.GetValue("LOG_DIR")
log_dir = log_dir if len(log_dir) > 0 and log_dir is not None else ""

state_logger = logging.getLogger("StateController")
state_logger.setLevel(logging.INFO)

handler = logging.FileHandler(f"{log_dir}StateController.log", mode='w')
console_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

state_logger.addHandler(console_handler)
state_logger.addHandler(handler)

state_logger.info(f"Logger for class StateController successfully created.")

class StateController:
    
    """
    Class for controlling States of bot. 
    
    It can:
    1. Set next State for current user;
    2. Add data to current user's state;
    3. Get added data;
    4. Reset all active States.
    
    Available methods:
    - SetNextState(self, state: Union[State, str]) -> None
    - AddDataState(self, **kwargs) -> None
    - GetDataState(self) -> dict
    - ResetStates(self) -> None
    """
    
    __contextState: asyncio.context.StateContext
    __logger: logging.Logger
    
    @property
    def ContextState(self): return self.__contextState;
    
    @property
    def Log(self):
        return self.__logger
    
    @Log.setter
    def Log(self, value: logging.Logger):
        self.__logger = value
    
    @ContextState.setter
    def ContextState(self, value: asyncio.context.StateContext | sync.context.StateContext): self.__contextState = value;
    
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)       
        
        instance.Log = state_logger
        return instance
    
    def __init__(self, contextState: asyncio.context.StateContext) -> None:
        self.Log.debug("Start initialization of state controller.")
        
        self.ContextState = contextState
        
        self.Log.debug("Initialization successfully completed.")
        
    async def SetNextState(self, state: Union[State, str]) -> None:
        await self.ContextState.set(state)
        self.Log.info(f"Setted new state \"{state}\" to user.")

    async def AddDataState(self, **kwargs) -> None:
        await self.ContextState.add_data(**kwargs)
        self.Log.info(f"Added some new data to user's state: {kwargs}.")

    async def GetDataState(self) -> dict:
        async with self.ContextState.data() as data:  # type: ignore
            self.Log.info(f"Successfully extracted data from current user's state.")
            return data

    async def ResetStates(self) -> None:
        await self.ContextState.delete()
        self.Log.info("Deleted all states for user.")