from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True, index=True)
    full_name = Column(String)
    username = Column(String)
    language_code = Column(String)
    level = Column(String, default="4")
    access_level = Column(String, default="basic")  # basic / extended / unlimited
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    voice_enabled = Column(Boolean, default=True)
    answer_voice_enabled = Column(Boolean, default=True)
    question_of_day = Column(Boolean, default=False)
    tip_of_day = Column(Boolean, default=False)

class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    level = Column(String)
    content = Column(Text)
    order = Column(Integer)

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    level = Column(String)  # 4 / 5
    question_en = Column(Text)
    question_ru = Column(Text)
    answer_en = Column(Text)
    answer_ru = Column(Text)

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True)
    title_en = Column(Text)
    title_ru = Column(Text)
    level = Column(String)
    sample_answer = Column(Text)

class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")
    questions_completed = Column(JSON, default=[])
    lessons_completed = Column(JSON, default=[])
    postponed_questions = Column(JSON, default=[])
    postponed_lessons = Column(JSON, default=[])
    emergencies_used = Column(Integer, default=0)
    exams_used = Column(Integer, default=0)

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
