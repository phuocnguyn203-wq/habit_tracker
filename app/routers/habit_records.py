from typing import Annotated
from fastapi import APIRouter, Path, Body, Depends, status
from app.dependencies import get_db

from app.schemas.habit_records import CreateHabitRecord
from sqlalchemy.orm import Session

from app.services import habit_records as habit_records_service

router = APIRouter(
    prefix='/habit_records',
    tags=['habit_records'],
)

@router.post('/create')
def create_habit_records(
    db: Annotated[Session, Depends(get_db)],
    create_habit_record: Annotated[CreateHabitRecord, Body()]   
):
    habit_records_service.create_record(
        db,
        create_habit_record
    )