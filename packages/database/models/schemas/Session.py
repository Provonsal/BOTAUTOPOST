import datetime
from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from packages.database.models import PostStatusesEnum, Posts, Sessions
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import _AsyncGeneratorContextManager


class Session:
    UserId: UUID
    Active: bool | None
    ExprireTime: datetime.datetime | None
    
    def __init__(self,
                 UserId: UUID | None,
                 Active: bool | None,
                 ExprireTime: datetime.datetime | None,
                 ):
        self.UserId = UserId if UserId is not None else uuid4()
        self.Active = Active
        self.ExprireTime = ExprireTime
        
    @classmethod
    def from_model(cls: "Session", model: Sessions) -> "Session":
        instanse = cls(
            model.UserId,
            model.Active,
            model.ExprireTime,
        )
        return instanse
    
    @staticmethod
    async def get(session: _AsyncGeneratorContextManager[AsyncSession], user_id: UUID):
        async with session as s:
            result = (await s.execute(select(Sessions).where(Sessions.UserId == user_id))).scalar()
            
        return Session.from_model(result) if result is not None else None
    
    async def update(self, session: _AsyncGeneratorContextManager[AsyncSession]) -> None: 
        updict = self.to_dict()
        
        if self.UserId is not None:
            async with session as s:
                await s.execute(update(Sessions).where(Sessions.UserId == self.UserId).values(updict))
        else:
            raise AttributeError()
    
    async def create(self, session: _AsyncGeneratorContextManager[AsyncSession]) -> None: 
        if self.UserId is not None:
            async with session as s:                    
                
                stmt2 = insert(Sessions).values(self.to_dict()).on_conflict_do_nothing()
                await s.execute(stmt2)
        else:
            raise AttributeError(name="debug")
        
    def to_dict(self) -> dict:
        return {
            "UserId" : self.UserId,
            "Active" : self.Active,
            "ExprireTime" : self.ExprireTime,
        }