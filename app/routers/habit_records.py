from typing import Annotated
from fastapi import APIRouter, Path, Body, Depends, status, HTTPException
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

@router.get('/{habit_id}')
def get_habit_records(
    db: Annotated[Session, Depends(get_db)],
    habit_id: int,
):
    results = habit_records_service.get_records(
        db,
        habit_id
    )
    return results

@router.put('/{record_id}')
def modify_habit_records(
    db: Annotated[Session, Depends(get_db)],
    record_id: Annotated[int, Path()],
    record: Annotated[CreateHabitRecord, Body()]
):
    try:
        habit_records_service.modify_record(
            db,
            record_id,
            record
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.delete('/{record_id}')
def delete_habit_record(
    db: Annotated[Session, Depends(get_db)],
    record_id: Annotated[int, Path()]
):
    try:
        habit_records_service.delete_record(
            db,
            record_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )