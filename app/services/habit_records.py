from sqlalchemy.orm import Session

from app.models.models import HabitRecord
from app.schemas.habit_records import CreateHabitRecord

def create_record(
    db: Session,
    create_habit_record: CreateHabitRecord
):
    habit_record = HabitRecord(**create_habit_record.model_dump())
    db.add(habit_record)
    db.commit()
    