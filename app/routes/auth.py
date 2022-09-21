from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.authentication.handler import access_security, refresh_security
from app.authentication.user_management import check_if_email_exists, create_user
from app.database.dependencies import get_db
from app.schemas.user import UserCreate

router = APIRouter()


@router.post("/signup")
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    if check_if_email_exists(db, user.email):
        raise HTTPException(
            status_code=400,
            detail="Email already in use.",
        )

    db_user = create_user(db, user=user)

    return {
        "user": db_user,
        "access_token": access_security.create_access_token(subject=db_user),
        "refresh_token": refresh_security.create_refresh_token(subject=db_user),
    }
