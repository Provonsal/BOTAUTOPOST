import datetime
from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from packages.database.models import PostStatusesEnum, Posts
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import _AsyncGeneratorContextManager


class Post:
    
    
    PostId: UUID
    ChatId: int | None
    UserId: UUID | None
    PostText: str | None
    ReactionListString: str | None
    PhotosIdListString: str | None
    TimeToPost: datetime.datetime | None
    PostStatus: PostStatusesEnum | None
    
    def __init__(self, 
                 PostId: UUID | None = None,
                 ChatId: int | None = None,
                 UserId: UUID | None = None,
                 PostText: str | None = None,
                 ReactionListString: str | None = None,
                 PhotosIdListString: str | None = None,
                 TimeToPost: datetime.datetime | None = None,
                 PostStatus: PostStatusesEnum | None = None,):
        
        self.PostId = PostId if PostId is not None else uuid4()
        self.ChatId = ChatId
        self.UserId = UserId
        self.PostText = PostText
        self.ReactionListString = ReactionListString
        self.PhotosIdListString = PhotosIdListString
        self.TimeToPost = TimeToPost
        self.PostStatus = PostStatus
        
    @classmethod
    def from_model(cls: "Post", model: Posts) -> "Post":
        instanse = cls(
            model.PostId,
            model.ChatId,
            model.UserId,
            model.PostText,
            model.ReactionListString,
            model.PhotosIdListString,
            model.TimeToPost,
            model.PostStatus
        )
        return instanse
    
    @staticmethod
    async def get(session: _AsyncGeneratorContextManager[AsyncSession], post_id: UUID):
        async with session as s:
            result = (await s.execute(select(Posts).where(Posts.PostId == post_id))).scalar()
            
        return Post.from_model(result) if result is not None else None
    
    @staticmethod
    async def get_by_user_id(session: _AsyncGeneratorContextManager[AsyncSession], user_id: UUID):
        async with session as s:
            result = (await s.execute(select(Posts).where(Posts.UserId == user_id))).scalar()
            
        return Post.from_model(result) if result is not None else None
    
    async def update(self, session: _AsyncGeneratorContextManager[AsyncSession]) -> None: 
        updict = self.to_dict()
        
        if self.PostId is not None:
            async with session as s:
                await s.execute(update(Post).where(Post.PostId == self.PostId).values(updict))
        else:
            raise AttributeError()
    
    async def create(self, session: _AsyncGeneratorContextManager[AsyncSession]) -> None: 
        if self.PostId is not None:
            async with session as s:                    
                
                stmt2 = insert(Post).values(self.to_dict()).on_conflict_do_nothing()
                await s.execute(stmt2)
        else:
            raise AttributeError(name="debug")
    
    def to_dict(self) -> dict:
        return {
            "PostId" : self.PostId,
            "ChatId" : self.ChatId,
            "UserId" : self.UserId,
            "PostText" : self.PostText,
            "ReactionListString" : self.ReactionListString,
            "PhotosIdListString" : self.PhotosIdListString,
            "TimeToPost" : self.TimeToPost,
            "PostStatus" : self.PostStatus
        }