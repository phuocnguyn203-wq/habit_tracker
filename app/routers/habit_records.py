from typing import Annotated
from fastapi import APIRouter, Path, Body, Depends, status, HTTPException
from app.dependencies import get_db
from app.dependencies import get_current_user

from app.models.models import User

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
    create_habit_record: Annotated[CreateHabitRecord, Body()],
    current_user: Annotated[User, Depends(get_current_user)],
):
    habit_records_service.create_record(
        db,
        create_habit_record,
        current_user.id,
    )

@router.get('/{habit_id}')
def get_habit_records(
    db: Annotated[Session, Depends(get_db)],
    habit_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
):
    results = habit_records_service.get_all_records_from_habit(
        db,
        habit_id,
        current_user.id,
    )
    return results

@router.put('/{record_id}')
def modify_habit_records(
    db: Annotated[Session, Depends(get_db)],
    record_id: Annotated[int, Path()],
    record: Annotated[CreateHabitRecord, Body()],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        habit_records_service.modify_record(
            db,
            record_id,
            record,
            current_user.id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.delete('/{record_id}')
def delete_habit_record(
    db: Annotated[Session, Depends(get_db)],
    record_id: Annotated[int, Path()],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        habit_records_service.delete_record(
            db,
            record_id,
            current_user.id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )