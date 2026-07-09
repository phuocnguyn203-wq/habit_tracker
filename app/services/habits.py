from app.schemas.habits import CreateHabit
from sqlalchemy.orm import Session
from app.models.models import Habit

from sqlalchemy import select

def create_habit(
    db: Session,
    create_habit: CreateHabit
):
    habit = Habit(**create_habit.model_dump())
    db.add(habit)
    db.commit()

def get_all_habits(
    db: Session,
):
    stmt = select(Habit)
    habits = db.scalars(stmt).all()
    return habits

def get_habit(
    db: Session,
    habit_id: int
):
    stmt = select(Habit).where(Habit.id==habit_id)
    result = db.execute(stmt).first()
    if result is not None:
        return result[0]
    else:
        return None