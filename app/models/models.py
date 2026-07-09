from typing import Optional
from app.database.database import Base

from datetime import datetime, UTC
from sqlalchemy import String, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Habit(Base):
    __tablename__ = 'habits'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey('users.id'))
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str]
    create_at: Mapped[datetime] = mapped_column(default=datetime.now(UTC))
    habit_records: Mapped[list['HabitRecord']] = relationship(back_populates='habit', cascade='all, delete-orphan')
    
class HabitRecord(Base):
    __tablename__ = 'habit_records'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    habit_id: Mapped[int] = mapped_column(ForeignKey('habits.id'))
    date: Mapped[datetime] = mapped_column(default=datetime.now(UTC))
    value: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(UTC))
    habit: Mapped['Habit'] = relationship(back_populates='habit_records')

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    hashed_password: Mapped[str]