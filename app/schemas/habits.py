from pydantic import BaseModel, Field
from datetime import datetime, UTC

class CreateHabit(BaseModel):
    name: str = Field(max_length=50)
    description: str
    create_at: datetime = Field(default=datetime.now(UTC))
    