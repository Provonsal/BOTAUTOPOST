from uuid import uuid4
from sqlalchemy import ARRAY, BIGINT, BOOLEAN, DATE, DATE, FLOAT, INTEGER, VARCHAR, TEXT, Column, Enum, ForeignKey

from .base import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from enum import Enum as Enumeration


class PostStatusesEnum(Enumeration):
    Planning = 0
    Posted = 1
    
class Users(Base):
    __tablename__ = "users"
    
    UserId = Column(UUID(as_uuid=True), primary_key=True, default=uuid4())
    TelegramId = Column(BIGINT, nullable=False)
    
    _pass_and_ques = relationship("PassANDQues", back_populates="_users")
    _users_groups_and_channels = relationship("UsersGoupsAndChannels", back_populates="_users")
    _posts = relationship("Posts", back_populates="_users")
    _sessions = relationship("Sessions", back_populates="_users")

class PassANDQues(Base):
    __tablename__ = "pass_and_ques"
    
    UserId = Column(UUID(as_uuid=True), ForeignKey("users.UserId"), primary_key=True)
    PassHash = Column(TEXT)
    QuestionAnswerHash = Column(TEXT)
    Question = Column(VARCHAR(100))
    
    _users = relationship("Users", back_populates="_pass_and_ques")
    
class UsersGoupsAndChannels(Base):
    __tablename__ = "users_groups_and_channels"
    
    UserId = Column(UUID(as_uuid=True), ForeignKey("users.UserId"), primary_key=True)
    ChatId = Column(BIGINT, unique=True)
    
    _users = relationship("Users", back_populates="_users_groups_and_channels")
    _posts = relationship("Posts", back_populates="_users_groups_and_channels")
    
class Posts(Base):
    __tablename__ = "posts"
    
    PostId = Column(UUID(as_uuid=True), primary_key=True, default=uuid4())
    ChatId = Column(BIGINT, ForeignKey("users_groups_and_channels.ChatId"), nullable=False)
    UserId = Column(UUID(as_uuid=True), ForeignKey("users.UserId"), nullable=False)
    PostText = Column(TEXT)
    ReactionListString = Column(TEXT)
    PhotosIdListString = Column(TEXT)
    TimeToPost = Column(DATE)
    PostStatus = Column(Enum(PostStatusesEnum))
    
    _users = relationship("Users", back_populates="_posts")
    _users_groups_and_channels = relationship("UsersGoupsAndChannels", back_populates="_posts")
    
class Sessions(Base):
    __tablename__ = "sessions"
    
    UserId = Column(UUID(as_uuid=True), ForeignKey("users.UserId"), primary_key=True)
    Active = Column(BOOLEAN, nullable=False)
    ExprireTime = Column(DATE)
    
    _users = relationship("Users", back_populates="_sessions")
