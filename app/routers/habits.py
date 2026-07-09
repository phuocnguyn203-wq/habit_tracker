from typing import Annotated
from sqlalchemy.orm import Session

from fastapi import APIRouter, Body, Path, Depends, HTTPException, status

from app.schemas.habits import CreateHabit
from app.dependencies import get_db

from app.services import habits as habit_service

router = APIRouter(
    prefix='/habits',
    tags=['habits'],
)

@router.post('/create_habit')
def create_habit(
    habit: Annotated[CreateHabit, Body()],
    db: Annotated[Session, Depends(get_db)]
):
    try:
        habit_service.create_habit(db, habit)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Something\'s wrong'
        )

@router.get('/get_all')
def get_all_habit(
    db: Annotated[Session, Depends(get_db)]
):
    habits = habit_service.get_all_habits(db)
    return habits

@router.get('/{habit_id}')
def get_habit(
    db: Annotated[Session, Depends(get_db)],
    habit_id: Annotated[int, Path()],
):
    habit = habit_service.get_habit(db, habit_id)
    return habit
