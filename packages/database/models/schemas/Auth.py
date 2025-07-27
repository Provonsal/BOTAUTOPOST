import datetime
from uuid import UUID, uuid4
import hashlib

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from packages.database.models import PassANDQues, PostStatusesEnum, Posts
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import _AsyncGeneratorContextManager


class Auth:
    UserId: UUID
    PassHash: str | None
    QuestionAnswerHash: str | None
    
    def __init__(self,
                 UserId: UUID | None,
                 PassHash: str | None,
                 QuestionAnswerHash: str | None):
        self.UserId = UserId if UserId is not None else uuid4()
        self.PassHash = PassHash
        self.QuestionAnswerHash = QuestionAnswerHash
        
    @classmethod
    def from_model(cls: "Auth", model: PassANDQues) -> "Auth":
        instanse = cls(
            model.UserId,
            model.PassHash,
            model.QuestionAnswerHash,
        )
        return instanse
    
    @staticmethod
    async def get(session: _AsyncGeneratorContextManager[AsyncSession], user_id: UUID):
        async with session as s:
            result = (await s.execute(select(PassANDQues).where(PassANDQues.UserId == user_id))).scalar()
            
        return Auth.from_model(result) if result is not None else None
    
    async def update(self, session: _AsyncGeneratorContextManager[AsyncSession]) -> None: 
        updict = self.to_dict()
        
        if self.UserId is not None:
            async with session as s:
                await s.execute(update(PassANDQues).where(PassANDQues.UserId == self.UserId).values(updict))
        else:
            raise AttributeError()
    
    async def create(self, session: _AsyncGeneratorContextManager[AsyncSession]) -> None: 
        if self.UserId is not None:
            async with session as s:                    
                
                stmt2 = insert(PassANDQues).values(self.to_dict()).on_conflict_do_nothing()
                await s.execute(stmt2)
        else:
            raise AttributeError(name="debug")
    
    async def validate_password(self, password: str) -> bool:
        if self.PassHash is not None:
            return self.PassHash == hashlib.sha256(password.encode()).hexdigest()
        else:
            raise AttributeError("Pass hash is empty.")
        
    async def validate_question(self, answer: str) -> bool:
        if self.QuestionAnswerHash is not None:
            return self.QuestionAnswerHash == hashlib.sha256(answer.encode()).hexdigest()
        else:
            raise AttributeError("Pass hash is empty.")
    
    def to_dict(self) -> dict:
        return {
            "UserId" : self.UserId,
            "PassHash" : self.PassHash,
            "QuestionAnswerHash" : self.QuestionAnswerHash
        }