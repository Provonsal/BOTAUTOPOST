

from packages.botapi.base_callback_route import BaseCallbackApiRoute
from packages.database import get_session
from packages.keyboard import InlineKeyboard
from telebot.types import InlineKeyboardButton


class Connection_CB(BaseCallbackApiRoute):
    def __init__(self):
        super().__init__(get_session)
        
        self.Func = lambda callback: callback.data == "connect_to"
        
        self.Text = "Подключение."
        
        inl_kb = InlineKeyboard()
        
        inl_kb += InlineKeyboardButton("join group", "https://t.me/NyashkaBot_1bot?startgroup=true&admin=change_info")
        inl_kb += InlineKeyboardButton("join channel", "https://t.me/NyashkaBot_1bot?startchannel=true&admin=change_info")
        inl_kb += InlineKeyboardButton("Назад", callback_data="mainmenu")
        
        self.Keyboard = inl_kb.Keyboard
        
    async def __call__(self, callback, state, bot):
        await super().__call__(callback, state, bot)
    
        await self.Botmas.edit_message(self.Text, self.UserId, self.UserMessage.id, self.Keyboard)