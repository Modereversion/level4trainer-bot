# database/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    full_name = Column(String, nullable=True)
    username = Column(String, nullable=True)
    language = Column(String, default='en')
    level = Column(String, default='level_4')
    voice_enabled = Column(Boolean, default=True)
    answer_enabled = Column(Boolean, default=True)
    question_of_the_day = Column(Boolean, default=False)
    tip_of_the_day = Column(Boolean, default=False)
    access_type = Column(String, default='regular')
    created_at = Column(DateTime, default=datetime.utcnow)


class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String, nullable=False)
    text_en = Column(Text, nullable=False)
    text_ru = Column(Text, nullable=False)
    answer_en = Column(Text, nullable=False)
    answer_ru = Column(Text, nullable=False)


class Lesson(Base):
    __tablename__ = 'lessons'

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)


class EmergencyCase(Base):
    __tablename__ = 'cases'

    id = Column(Integer, primary_key=True, index=True)
    text_en = Column(Text, nullable=False)
    text_ru = Column(Text, nullable=False)
    sample_answer_en = Column(Text, nullable=True)


class Feedback(Base):
    __tablename__ = 'feedbacks'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserProgress(Base):
    __tablename__ = 'progress'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    question_id = Column(Integer, nullable=True)
    lesson_id = Column(Integer, nullable=True)
    case_id = Column(Integer, nullable=True)
    exam_score = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
