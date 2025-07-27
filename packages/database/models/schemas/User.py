from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from packages.database.models import PassANDQues, Users, UsersGoupsAndChannels
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import _AsyncGeneratorContextManager


class User:
    UserId: UUID
    TelegramId: int
    ConnectedChat: int | None
    
    def __init__(self, telegramid: int, user_id: UUID | None = None):
        self.TelegramId = telegramid
        self.UserId = user_id if user_id is not None else uuid4()
        
    @classmethod
    def from_model(cls: "User", model: Users) -> "User":
        instanse = cls(model.TelegramId, 
                       model.UserId)
        return instanse
    
    @staticmethod
    async def get(session: _AsyncGeneratorContextManager[AsyncSession], user_id: UUID):
        async with session as s:
            result = (await s.execute(select(Users).where(Users.UserId == user_id))).scalar()
            
        return User.from_model(result) if result is not None else None
    
    @staticmethod
    async def get_by_telegram_id(session: _AsyncGeneratorContextManager[AsyncSession], telegram_id: int):
        async with session as s:
            result = (await s.execute(select(Users).where(Users.TelegramId == telegram_id))).scalar()
            
        return User.from_model(result) if result is not None else None
    
    async def update(self, session: _AsyncGeneratorContextManager[AsyncSession]) -> None: 
        updict = self.to_dict()
        
        if self.UserId is not None:
            async with session as s:
                await s.execute(update(Users).where(Users.UserId == self.UserId).values(updict))
        else:
            raise AttributeError()
    
    async def create(self, session: _AsyncGeneratorContextManager[AsyncSession]) -> None: 
        if self.UserId is not None:
            async with session as s:                    
                
                stmt2 = insert(Users).values(self.to_dict()).on_conflict_do_nothing()
                await s.execute(stmt2)
        else:
            raise AttributeError(name="debug")
    
    async def get_user_connected_chat_id(self, session: _AsyncGeneratorContextManager[AsyncSession]):
        
        async with session as s:
            result = (await s.execute(select(UsersGoupsAndChannels.ChatId).where(UsersGoupsAndChannels.UserId == self.UserId))).scalar()
            if result is not None:
                self.ConnectedChat = result
                return self.ConnectedChat
            else:
                return result
            
    async def get_user_question(self, session: _AsyncGeneratorContextManager[AsyncSession]):
        
        async with session as s:
            result = (await s.execute(select(PassANDQues.Question).where(PassANDQues.UserId == self.UserId))).scalar()
            
            return result
    
    def to_dict(self) -> dict:
        return {
            "UserId" : self.UserId,
            "TelegramId" : self.TelegramId
        }