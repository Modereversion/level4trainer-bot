from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    full_name = Column(String)
    username = Column(String)
    language = Column(String, default="en")
    level = Column(String, default="4")
    tts_enabled = Column(Boolean, default=True)
    tts_answers = Column(Boolean, default=True)
    question_of_day = Column(Boolean, default=False)
    tip_of_day = Column(Boolean, default=False)
    access_level = Column(String, default="basic")  # basic, extended, unlimited
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    progress = relationship("Progress", back_populates="user")
    feedback = relationship("Feedback", back_populates="user")


class Progress(Base):
    __tablename__ = 'progress'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lesson_index = Column(Integer, default=0)
    current_question_id = Column(String)
    level = Column(String)
    questions_done = Column(Integer, default=0)
    cases_done = Column(Integer, default=0)
    exams_done = Column(Integer, default=0)
    questions_postponed = Column(Text, default="")
    topics_postponed = Column(Text, default="")
    user = relationship("User", back_populates="progress")


class Feedback(Base):
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    reply = Column(Text, default="")
    timestamp = Column(DateTime, default=func.now())
    user = relationship("User", back_populates="feedback")
