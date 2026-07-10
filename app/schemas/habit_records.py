from pydantic import BaseModel

from datetime import datetime

class CreateHabitRecord(BaseModel):
    habit_id: int
    date: datetime
    value: float