from packages.botapi.base_route import BaseBotRoute
from packages.database import get_session
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberUpdated


class MainStart(BaseBotRoute):
    def __init__(self):
        
        super().__init__(get_session)
        
        self.Commands = ["start"]
        
    async def __call__(self, message, state, bot):
        await super().__call__(message, state, bot)
        
        
        
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(InlineKeyboardButton("join group", "https://t.me/NyashkaBot_1bot?startgroup=true&admin=change_info"))
        kb.add(InlineKeyboardButton("join channel", "https://t.me/NyashkaBot_1bot?startchannel=true&admin=change_info"))
        
        
        
        await self.Botmas.send_message(self.UserId, "test string", kb)
        
        