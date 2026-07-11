from app.schemas.habits import CreateHabit
from sqlalchemy.orm import Session
from app.models.models import Habit

from sqlalchemy import select

def create_habit(
    db: Session,
    create_habit: CreateHabit,
    user_id: int
):
    habit = Habit(**create_habit.model_dump(), user_id=user_id)
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit

def get_all_habits(
    db: Session,
    user_id: int,
):
    stmt = select(Habit).where(Habit.user_id==user_id)
    habits = db.scalars(stmt).all()
    return habits

def get_habit(
    db: Session,
    habit_id: int,
    user_id: int,
):
    stmt = select(Habit).where(Habit.id==habit_id).where(Habit.user_id==user_id)
    result = db.execute(stmt).first()
    if result is not None:
        return result[0]
    else:
        raise ValueError(f'Habit {habit_id} does not exist')

def modify_habit(
    db: Session,
    habit_id: int,
    user_id: int,
    modify_habit: CreateHabit
):
    stmt = select(Habit).where(Habit.id==habit_id).where(Habit.user_id==user_id)
    result = db.execute(stmt).first()
    if result is not None:
        habit = result[0]
        modify_dict = modify_habit.model_dump()
        for k, v in modify_dict.items():
            setattr(habit, k, v)
        db.commit()
        db.refresh(habit)
        return habit
    else:
        raise ValueError(f'Habit {habit_id} does not exist')

def delete_habit(
    db: Session,
    user_id: int,
    habit_id: int,
):
    result = db.execute(select(Habit).where(Habit.id==habit_id).where(Habit.user_id==user_id)).first()
    if result is not None:
        habit = result[0]
        db.delete(habit)
        db.commit()
    else:
        raise ValueError(f'Habit {habit_id} does not exist')