from typing import Annotated
from sqlalchemy.orm import Session
from app.models.models import User

from fastapi import APIRouter, Body, Path, Depends, HTTPException, status

from app.schemas.habits import CreateHabit
from app.dependencies import get_db
from app.dependencies import get_current_user

from app.services import habits as habit_service

router = APIRouter(
    prefix='/habits',
    tags=['habits'],
)

@router.post('/create_habit')
def create_habit(
    habit: Annotated[CreateHabit, Body()],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        habit_service.create_habit(
            db,
            habit,
            current_user.id,
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Something\'s wrong'
        )

@router.get('/get_all')
def get_all_habit(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    habits = habit_service.get_all_habits(
        db,
        current_user.id,
    )
    return habits

@router.get('/{habit_id}')
def get_habit(
    db: Annotated[Session, Depends(get_db)],
    habit_id: Annotated[int, Path()],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        habit = habit_service.get_habit(
            db,
            habit_id,
            current_user.id,)
        return habit
    except ValueError as e:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
@router.put('/{habit_id}')
def modify_habit(
    db: Annotated[Session, Depends(get_db)],
    habit_id: Annotated[int, Path()],
    modify_habit: Annotated[CreateHabit, Body()],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        habit_service.modify_habit(
            db,
            habit_id,
            current_user.id,
            modify_habit
        )
    except ValueError as e:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.delete('/{habit_id}')
def delete_habit(
    db: Annotated[Session, Depends(get_db)],
    habit_id: Annotated[int, Path()],
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        habit_service.delete_habit(
            db,
            current_user.id,
            habit_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )