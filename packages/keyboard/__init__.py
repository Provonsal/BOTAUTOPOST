from typing import Iterable
from telebot.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton




class ReplyKeyboard:
    
    __keyboard: ReplyKeyboardMarkup
    __buttonsCollection: list[KeyboardButton | list[KeyboardButton]]

    def __init__(
        self,
        resizeKeyboard: bool | None = None,
        oneTimeKeyboard: bool | None = None,
        selective: bool | None = None,
        rowWidth: int = 1,
        inputFieldPlaceholder: str | None = None,
        isPersistent: bool | None = None
    ) -> None:

        self.__buttonsCollection = []

        self.Keyboard = ReplyKeyboardMarkup(
            resizeKeyboard,
            oneTimeKeyboard,
            selective,
            rowWidth,
            inputFieldPlaceholder,
            isPersistent
        )
        
        return

    @property
    def Keyboard(self):
        """"""
        return self.__keyboard
    
    @property
    def ButtonsCollection(self):
        """"""
        return self.__buttonsCollection

    @Keyboard.setter
    def Keyboard(self, value):
        """"""
        self.__keyboard = value
    
    @ButtonsCollection.setter
    def ButtonsCollection(self, value):
        """"""
        self.__buttonsCollection = value

    # operator +=
    def __iadd__(self, buttons: list[KeyboardButton] | KeyboardButton) -> "ReplyKeyboard":
        if isinstance(buttons, KeyboardButton):
            self.Keyboard.add(buttons)
            self.ButtonsCollection.append(buttons)
        elif isinstance(buttons, list):
            self.AddButtons(buttons)
        return self

    # operator *=
    def __imul__(self, buttons: list[KeyboardButton] | KeyboardButton) -> "ReplyKeyboard":
        if isinstance(buttons, KeyboardButton):
            self.Keyboard.row(buttons)
            self.__buttonsCollection.append([buttons])
        elif isinstance(buttons, list):
            self.AddButtons(buttons)
        else:
            raise TypeError()
        return self

    # public
    def AddButtons(self, buttons: list[KeyboardButton]) -> None:
        self.Keyboard.add(*buttons)
        self.ButtonsCollection.append(buttons)

    def AddRow(self, buttons: list[KeyboardButton]) -> None:
        self.Keyboard.row(*buttons)
        self.ButtonsCollection.append(buttons)
    
class InlineKeyboard:
    
    __keyboard: InlineKeyboardMarkup
    __buttonsCollection: list
    
    def __init__(self, row_width: int = 1) -> None:
        self.Keyboard = InlineKeyboardMarkup(row_width=row_width)
        self.ButtonsCollection = []
    
    @property
    def Keyboard(self):
        """"""
        return self.__keyboard
    
    @property
    def ButtonsCollection(self):
        """"""
        return self.__buttonsCollection

    @Keyboard.setter
    def Keyboard(self, value):
        """"""
        self.__keyboard = value
    
    @ButtonsCollection.setter
    def ButtonsCollection(self, value):
        """"""
        self.__buttonsCollection = value
    
    # operator +=
    def __iadd__(self, buttons: Iterable[InlineKeyboardButton] | InlineKeyboardButton) -> "InlineKeyboard":
        self.add_buttons(buttons)
        return self

    # operator *=
    def __imul__(self, buttons: Iterable[InlineKeyboardButton] | InlineKeyboardButton) -> "InlineKeyboard":
        self.add_row(buttons)
        return self

    # public 
    def add_buttons(self, buttons: Iterable[InlineKeyboardButton] | InlineKeyboardButton) -> None:
        if isinstance(buttons, Iterable):
            self.Keyboard.add(*buttons)
        elif isinstance(buttons, InlineKeyboardButton):
            self.Keyboard.add(buttons)
        else:
            raise TypeError()
    
    def add_row(self, buttons: Iterable[InlineKeyboardButton] | InlineKeyboardButton) -> None:
        if isinstance(buttons, Iterable):
            self.Keyboard.row(*buttons)
        elif isinstance(buttons, InlineKeyboardButton):
            self.Keyboard.row(buttons)
        else:
            raise TypeError()