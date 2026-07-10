from sqlalchemy.orm import Session

from sqlalchemy import select

from app.models.models import HabitRecord
from app.schemas.habit_records import CreateHabitRecord

def create_record(
    db: Session,
    create_habit_record: CreateHabitRecord
):
    habit_record = HabitRecord(**create_habit_record.model_dump())
    db.add(habit_record)
    db.commit()

def get_records(
    db: Session,
    habit_id: int
):
    stmt = select(HabitRecord).where(HabitRecord.habit_id==habit_id)
    results = db.execute(stmt).scalars().all()
    return results

def modify_record(
    db: Session,
    record_id: int,
    new_record: CreateHabitRecord,
):
    stmt = select(HabitRecord).where(HabitRecord.id==record_id)
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
    record_id: int
):
    record = db.scalars(
        select(HabitRecord).where(HabitRecord.id==record_id)
    ).one()
    
    if not record:
        raise ValueError(f'Habit Record {record_id} does not exist')
    else:
        db.delete(record)
        db.commit()