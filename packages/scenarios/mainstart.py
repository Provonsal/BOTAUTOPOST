from packages.botapi.base_callback_route import BaseCallbackApiRoute
from packages.botapi.base_route import BaseBotRoute
from packages.database import get_session
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberUpdated

from packages.database.models.schemas.User import User
from packages.database.models.schemas.Session import Session as SessionScheme
from packages.keyboard import InlineKeyboard

# kb = InlineKeyboardMarkup(row_width=1)
# kb.add(InlineKeyboardButton("join group", "https://t.me/NyashkaBot_1bot?startgroup=true&admin=change_info"))
# kb.add(InlineKeyboardButton("join channel", "https://t.me/NyashkaBot_1bot?startchannel=true&admin=change_info"))
        
        
class MainStart_API(BaseBotRoute):
    def __init__(self):
        
        super().__init__(get_session)
        
        self.Commands = ["start"]
        
        self.text_message = "Здравствуйте. Чем могу быть полезен?"

        kb = InlineKeyboard()
        kb += InlineKeyboardButton("Мои посты.", callback_data="my_posts")
        kb += InlineKeyboardButton("Составить пост", callback_data="make_post")
        kb += InlineKeyboardButton("Подключить бот к группе", callback_data="connect_to")

        self.Keyboard = kb.Keyboard
        
    async def __call__(self, message, state, bot):
        await super().__call__(message, state, bot)
        
        await self.StateControl.ResetStates()
        
        user = await User.get_by_telegram_id(self.Session, self.UserId)
        
        if user is None:
            
            user = User(self.UserId)
            await user.create(self.Session)
        
        await self.Botmas.send_message(self.UserId, self.text_message, self.Keyboard)
        
        
class MainStart_CB(BaseCallbackApiRoute):
    
    def __init__(self):
        super().__init__(get_session)
        
        self.Func = lambda callback: callback.data == "mainmenu"
        
        self.text_message = "Здравствуйте. Чем могу быть полезен?"

        kb = InlineKeyboard()
        kb += InlineKeyboardButton("Мои посты.", callback_data="my_posts")
        kb += InlineKeyboardButton("Составить пост", callback_data="make_post")
        kb += InlineKeyboardButton("Подключить бот к группе", callback_data="connect_to")

        self.Keyboard = kb.Keyboard
        
    async def __call__(self, callback, state, bot):
        await super().__call__(callback, state, bot)
    
        await self.StateControl.ResetStates()
        
        user = await User.get_by_telegram_id(self.Session, self.UserId)
        
        if user is None:
            
            user = User(self.UserId)
            await user.create(self.Session)
        
        await self.Botmas.edit_message(self.text_message, self.UserId, self.UserMessage.id, self.Keyboard)