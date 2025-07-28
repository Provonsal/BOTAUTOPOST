from datetime import datetime
from packages.botapi.base_callback_route import BaseCallbackApiRoute
from packages.botapi.base_route import BaseBotRoute
from packages.database import get_session
from packages.database.models import PostStatusesEnum
from packages.database.models.schemas.Post import Post
from packages.database.models.schemas.User import User
from packages.keyboard import InlineKeyboard, ReplyKeyboard
from telebot.states.asyncio.context import State
from telebot.states import StatesGroup

from telebot.types import InlineKeyboardButton, KeyboardButton, InputMediaPhoto


class MakingPostStateGroup(StatesGroup):
    GotPostText = State()
    SplitChoice = State()
    GotPostPhoto = State()
    CheckingPost = State()
    TimeChoice = State()
    
    

class MakePostEnterText_CB(BaseCallbackApiRoute):
    
    """
    **Этап номер №1**.  
    Начальный рут создания поста.  
    
    ---
    Этап принятия текста поста.
    """
    
    def __init__(self):
        super().__init__(get_session)
        
        self.Func = lambda callback: callback.data == "make_post"
        
        self.Text = "Отправьте мне текст нового поста."
        
        keyboard = InlineKeyboard()
        keyboard += InlineKeyboardButton("Назад", callback_data="mainmenu")
        
        self.Keyboard = keyboard.Keyboard
        
    async def __call__(self, callback, state, bot):
        await super().__call__(callback, state, bot)
        
        await self.Botmas.edit_message(self.Text, self.UserId, self.UserMessage.id, self.Keyboard)
        await self.StateControl.SetNextState(MakingPostStateGroup.GotPostText)
        
class MakePostGotText(BaseBotRoute):
    
    """
    **Этап номер №2**.  
    Этап принятия фото для поста.  
    
    ---
    Пользователю дается выбор, добавить фото к посту или нет.  
    На этом этапе хендлеры разделяются на 2 пути.
    """
    
    def __init__(self):
        super().__init__(get_session)
        
        self.StatmentState = MakingPostStateGroup.GotPostText
        
        self.Text = "Отправьте пожалуйсто фото для поста (не обязательно)."
        
        keyboard = ReplyKeyboard(oneTimeKeyboard=True, resizeKeyboard=True)
        
        keyboard.Keyboard.add(KeyboardButton("Пропустить")) 
        
        self.Keyboard = keyboard.Keyboard
        
    async def __call__(self, message, state, bot):
        await super().__call__(message, state, bot)
        
        await self.StateControl.AddDataState(PostText=self.UserMessage.text)
        
        await self.Botmas.send_message(self.UserId, self.Text, self.Keyboard)
        
        await self.StateControl.SetNextState(MakingPostStateGroup.SplitChoice)
        
class MakePostSkippedPhoto(BaseBotRoute):
    
    """
    **Этап номер №4.1**.  
    Этап пропуска добавления фото после отправления текста.  
    
    ---
    Мы попадаем в это альтернативное меню если пользователь  
    выбрал пропустить добавление фото.
    """
    
    def __init__(self):
        super().__init__(get_session)
        
        self.Regexp = "Пропустить"
        
        self.StatmentState = MakingPostStateGroup.SplitChoice
        
        keyboard = ReplyKeyboard(oneTimeKeyboard=True, resizeKeyboard=True)
        keyboard += KeyboardButton("Подтверждаю")
        keyboard.AddRow([KeyboardButton("Изменить текст"), KeyboardButton("Изменить фото")])
        keyboard += KeyboardButton("Отменить")
        
        self.Keyboard = keyboard.Keyboard
        
    async def __call__(self, message, state, bot):
        await super().__call__(message, state, bot)
        
        saved_text = (await self.StateControl.GetDataState())["PostText"]
        
        if len(saved_text) == 0:
            saved_text = "NO TEXT FOUND"
            
        await self.StateControl.SetNextState(MakingPostStateGroup.CheckingPost)
        
        await self.Botmas.send_message(self.UserId, "Пожалуйста проверьте содержимое поста.")
        
        # Отправить итоговый пост с текстом, без фото 
        await self.Botmas.send_message(self.UserId, saved_text, self.Keyboard)
        
        
class MakePostRetryText(BaseBotRoute):
    
    """
    **Этап номер №1.5**.  
    Этап повторного принятия текста для поста.  
    
    ---
    Это возвращает нас назад к моменту выбора текста,  
    после него пойдет выбор фото как по порядку.
    """
    
    def __init__(self):
        super().__init__(get_session)
        
        self.StatmentState = MakingPostStateGroup.CheckingPost
        self.Regexp = "Изменить текст"
        
        self.Text = "Отправьте мне текст нового поста."
        
    async def __call__(self, message, state, bot):
        await super().__call__(message, state, bot)
        
        await self.Botmas.send_message(self.UserId, self.Text)
        
        await self.StateControl.SetNextState(MakingPostStateGroup.GotPostText)
        
class MakePostRetryPhotos(BaseBotRoute):
    
    """
    **Этап номер №2.5**.  
    Этап повторного выбора фото для поста.  
    
    ---
    Это возвращает нас назад к моменту выбора фото,  
    после него все пойдет по порядку.
    """
    
    def __init__(self):
        super().__init__(get_session)
        
        self.StatmentState = MakingPostStateGroup.CheckingPost
        self.Regexp = "Изменить фото"
        
        self.Text = "Отправьте пожалуйсто фото для поста (не обязательно)."
        
        keyboard = ReplyKeyboard(oneTimeKeyboard=True, resizeKeyboard=True)
        keyboard += KeyboardButton("Пропустить")
        
        self.Keyboard = keyboard.Keyboard
        
    async def __call__(self, message, state, bot):
        await super().__call__(message, state, bot)
        
        await self.Botmas.send_message(self.UserId, self.Text, self.Keyboard)
        
        await self.StateControl.SetNextState(MakingPostStateGroup.GotPostPhoto)
        

class MakePostGotPhoto(BaseBotRoute):
    
    """
    **Этап номер №3**.  
    Этап получения ботом фотографий.  
    
    ---
    На этом этапе пользователь отсылает боту фото, после чего,  
    если все фото загружены, пользователь жмет кнопку \"Нужные фото загружены\".
    
    """
    
    def __init__(self):
        super().__init__(get_session)
        
        self.ContentTypes = ['photo']
        self.StatmentState = MakingPostStateGroup.GotPostPhoto
        
        keyboard = ReplyKeyboard(oneTimeKeyboard=True, resizeKeyboard=True)
        keyboard += KeyboardButton("Нужные фото загружены")
        
        
        self.Keyboard = keyboard.Keyboard
        
    async def __call__(self, message, state, bot):
        
        await super().__call__(message, state, bot)
        
        media_group_id = (await self.StateControl.GetDataState()).get("PostPhotoMediaGroupId")
        
        if media_group_id is None or len(media_group_id) == 0:
            await self.StateControl.AddDataState(PostPhotoMediaGroupId=self.UserMessage.media_group_id)
        elif media_group_id == self.UserMessage.media_group_id:
            return
            
        photo_string = ""
        for photo in self.UserMessage.photo:
            photo_string += photo.file_id + ";"
            
        await self.StateControl.AddDataState(PostPhoto=photo_string)
        
        await self.Botmas.send_message(self.UserId, "Фото успешно сохранены.", self.Keyboard)
        
class MakePostGotPhotoSplit(BaseBotRoute):
    
    """
    **Этап номер №3.5**.  
    Этап получения ботом фотографий в случае не пропуска добавления фото в начале.  
    
    ---
    На этом этапе пользователь отсылает боту фото, после чего,  
    если все фото загружены, пользователь жмет кнопку \"Нужные фото загружены\".
    
    """
    
    def __init__(self):
        super().__init__(get_session)
        
        self.ContentTypes = ['photo']
        self.StatmentState = MakingPostStateGroup.SplitChoice
        
        keyboard = ReplyKeyboard(oneTimeKeyboard=True, resizeKeyboard=True)
        keyboard += KeyboardButton("Нужные фото загружены")
        
        
        self.Keyboard = keyboard.Keyboard
        
    async def __call__(self, message, state, bot):
        
        await super().__call__(message, state, bot)
        
        media_group_id = (await self.StateControl.GetDataState()).get("PostPhotoMediaGroupId")
        
        if media_group_id is None or len(media_group_id) == 0:
            await self.StateControl.AddDataState(PostPhotoMediaGroupId=self.UserMessage.media_group_id)
        elif media_group_id == self.UserMessage.media_group_id:
            return
            
        photo_string = ""
        for photo in self.UserMessage.photo:
            photo_string += photo.file_id + ";"
            
        await self.StateControl.AddDataState(PostPhoto=photo_string)
        
        await self.Botmas.send_message(self.UserId, "Фото успешно сохранены.", self.Keyboard)
        
class MakePostConfirmedPhoto(BaseBotRoute):
    
    """
    **Этап номер №4.2**.  
    Этап проверки содержимого поста и его внешнего вида в случае изменения фото.  
    
    ---
    На этом этапе пользователь решает, надо ли ему менять текст или фото поста,  
    в случае если его все устраивает, он нажимает кнопку **\"Подтверждаю\"**,  
    в иных случаях кнопки **\"Изменить текст\"**, **\"Изменить фото\"** и **\"Отменить\"** соответственно.
    
    """
    
    def __init__(self):
        super().__init__(get_session)
        
        self.Regexp = "Нужные фото загружены"
        self.StatmentState = MakingPostStateGroup.GotPostPhoto
        keyboard = ReplyKeyboard(oneTimeKeyboard=True, resizeKeyboard=True)
        keyboard += KeyboardButton("Подтверждаю")
        keyboard.AddRow([KeyboardButton("Изменить текст"), KeyboardButton("Изменить фото")])
        keyboard += KeyboardButton("Отменить")
        
        self.Keyboard = keyboard.Keyboard
        
    async def __call__(self, message, state, bot):
        await super().__call__(message, state, bot)
        
        await self.StateControl.AddDataState(PostPhotoMediaGroupId="")
        await self.StateControl.SetNextState(MakingPostStateGroup.CheckingPost)
        
        saved_text = (await self.StateControl.GetDataState())["PostText"]
        
        if len(saved_text) == 0:
            saved_text = "NO TEXT FOUND"
            
        photo: str = (await self.StateControl.GetDataState())["PostPhoto"]
        
        if photo[-1] == ";":
            photo_list = photo[:-1].split(";")
        else:
            photo_list = photo.split(";")
        
        photo_media_list = [InputMediaPhoto(file_id) for file_id in photo_list]
        
        photo_media_list[0].caption = saved_text
        
        await self.Botmas.send_message(self.UserId, "Пожалуйста проверьте содержимое поста.", self.Keyboard)
        
        await self.Botmas.Bot.send_media_group(self.UserId, photo_media_list)
        

class MakePostConfirmedPhotoSplit(BaseBotRoute):
    
    """
    **Этап номер №4**.  
    Этап проверки содержимого поста и его внешнего вида в случае,  
    если пользователь ничего не изменял и не возвращался.  
    
    ---
    На этом этапе пользователь решает, надо ли ему менять текст или фото поста,  
    в случае если его все устраивает, он нажимает кнопку **\"Подтверждаю\"**,  
    в иных случаях кнопки **\"Изменить текст\"**, **\"Изменить фото\"** и **\"Отменить\"** соответственно.
    
    """
    
    def __init__(self):
        super().__init__(get_session)
        
        self.Regexp = "Нужные фото загружены"
        self.StatmentState = MakingPostStateGroup.SplitChoice
        keyboard = ReplyKeyboard(oneTimeKeyboard=True, resizeKeyboard=True)
        keyboard += KeyboardButton("Подтверждаю")
        keyboard.AddRow([KeyboardButton("Изменить текст"), KeyboardButton("Изменить фото")])
        keyboard += KeyboardButton("Отменить")
        
        self.Keyboard = keyboard.Keyboard
        
    async def __call__(self, message, state, bot):
        await super().__call__(message, state, bot)
        
        await self.StateControl.AddDataState(PostPhotoMediaGroupId="")
        await self.StateControl.SetNextState(MakingPostStateGroup.CheckingPost)
        
        saved_text = (await self.StateControl.GetDataState())["PostText"]
        
        if len(saved_text) == 0:
            saved_text = "NO TEXT FOUND"
            
        photo: str = (await self.StateControl.GetDataState())["PostPhoto"]
        
        if photo[-1] == ";":
            photo_list = photo[:-1].split(";")
        else:
            photo_list = photo.split(";")
        
        photo_media_list = [InputMediaPhoto(file_id) for file_id in photo_list]
        
        photo_media_list[0].caption = saved_text
        
        await self.Botmas.send_message(self.UserId, "Пожалуйста проверьте содержимое поста.", self.Keyboard)
        
        await self.Botmas.Bot.send_media_group(self.UserId, photo_media_list)
        
class MakePostConfirmedPostView(BaseBotRoute):
    
    """
    **Этап номер №5**.  
    Этап выбора пользователем времени.  
    
    ---
    На этом этапе пользователь решает, когда нужно опубликовать пост.
    
    """
    
    def __init__(self):
        super().__init__(get_session)
        
        self.Regexp = "Подтверждаю"
        self.StatmentState = MakingPostStateGroup.CheckingPost
        
        self.Text = "Когда вы хотите опубликовать пост?"
        
        keyboard = InlineKeyboard()
        keyboard += InlineKeyboardButton("Сейчас", callback_data="post_now")
        keyboard += InlineKeyboardButton("Через промежуток времени", callback_data="post_in_some_time")
        keyboard += InlineKeyboardButton("В конкретное время", callback_data="post_at_concrete_datetime")
        
        self.Keyboard = keyboard.Keyboard
        
    async def __call__(self, message, state, bot):
        await super().__call__(message, state, bot)
        
        await self.StateControl.SetNextState(MakingPostStateGroup.TimeChoice)
        
        await self.Botmas.send_message(self.UserId, self.Text, self.Keyboard)
        
        
class MakePostTimeChoiseNow(BaseCallbackApiRoute):
    
    def __init__(self):
        super().__init__(get_session)
        
        self.Func = lambda callback: callback.data == "post_now"
        self.StatmentState = MakingPostStateGroup.TimeChoice
        keyboard = InlineKeyboard()
        keyboard += InlineKeyboardButton("Назад в меню", callback_data="mainmenu")
        self.Keyboard = keyboard.Keyboard
        
        
    async def __call__(self, callback, state, bot):
        await super().__call__(callback, state, bot)
        
        post_text = (await self.StateControl.GetDataState())["PostText"]
        
        if len(post_text) == 0:
            post_text = "NO TEXT FOUND"
            
        photo: str = (await self.StateControl.GetDataState())["PostPhoto"]
        
        user = await User.get_by_telegram_id(self.Session, self.UserId)
        
        post = Post(
            ChatId=user.ConnectedChat,
            UserId=user.UserId,
            PostText=post_text,
            PhotosIdListString=photo,
            TimeToPost=datetime.now(),
            PostStatus=PostStatusesEnum.Posted
        )
        
        await post.create(self.Session)
        
        if len(photo) == 0:
            await self.Botmas.send_message(user.get_user_connected_chat_id(), post_text)
        else:
            if photo[-1] == ";":
                photo_list = photo[:-1].split(";")
            else:
                photo_list = photo.split(";")
            
            photo_media_list = [InputMediaPhoto(file_id) for file_id in photo_list]
            
            photo_media_list[0].caption = post_text
            
            await self.Botmas.Bot.send_media_group(user.get_user_connected_chat_id(), photo_media_list)
        
        await self.Botmas.edit_message("Пост опубликован")
        
