from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    spotify_id = Column(String, unique=True)
    display_name = Column(String)

    access_tokens = relationship("AccessToken", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    session_tokens = relationship("SessionToken", back_populates="user")

class AccessToken(Base):
    __tablename__ = "access_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    access_token = Column(String)
    expires_at = Column(DateTime)

    user = relationship("User", back_populates="access_tokens")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    refresh_token = Column(String)
    #expires_at = Column(DateTime)

    user = relationship("User", back_populates="refresh_tokens")
 
class SessionToken(Base):
    __tablename__ = "session_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_token = Column(String)
    #expires_at = Column(DateTime)

    user = relationship("User", back_populates="session_tokens")


