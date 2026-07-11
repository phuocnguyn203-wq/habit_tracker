from sqlalchemy.orm import Session

from sqlalchemy import select

from app.models.models import HabitRecord, Habit
from app.schemas.habit_records import CreateHabitRecord

def create_record(
    db: Session,
    create_habit_record: CreateHabitRecord,
    user_id: int
):
    #find habit
    stmt = select(Habit)\
        .where(Habit.id==create_habit_record.habit_id)
    habit = db.execute(stmt).scalar_one()
    if not habit:
        raise ValueError(f'Habit {create_habit_record.habit_id} does not exist')
    elif habit.user_id == user_id:
        habit_record = HabitRecord(**create_habit_record.model_dump())
        db.add(habit_record)
        db.commit()
    else:
        raise ValueError(f'Wrong user_id')
    
def get_all_records_from_habit(
    db: Session,
    habit_id: int,
    user_id,
):
    stmt = select(HabitRecord).\
        select_from(HabitRecord)\
            .join(Habit, HabitRecord.habit_id==Habit.id)\
                .where(HabitRecord.habit_id==habit_id)\
                    .where(Habit.user_id==user_id)
    results = db.execute(stmt).scalars().all()
    return results

def modify_record(
    db: Session,
    record_id: int,
    new_record: CreateHabitRecord,
    user_id: int,
):
    stmt = select(HabitRecord)\
        .select_from(HabitRecord)\
            .join(Habit, HabitRecord.habit_id==Habit.id)\
                .where(Habit.user_id==user_id)\
                    .where(Habit.id==record_id)
    result = db.execute(stmt).first()
    if result is None:
        raise ValueError(f'Habit Record {record_id} does not exist')
    else:
        record = result[0]
        record_dict = new_record.model_dump()
        for k, v in record_dict.items():
            setattr(record, k, v)
        db.commit()

def delete_record(
    db: Session,
    record_id: int,
    user_id: int,
):
    stmt = select(HabitRecord)\
        .select_from(HabitRecord)\
            .join(Habit, HabitRecord.habit_id==Habit.id)\
                .where(Habit.user_id==user_id)\
                    .where(HabitRecord.id==record_id)
    record = db.scalars(
        stmt
    ).one()
    
    if not record:
        raise ValueError(f'Habit Record {record_id} does not exist')
    else:
        db.delete(record)
        db.commit()