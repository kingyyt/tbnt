from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.db.repository import get_db
from app.models.user import User as UserModel
from app.api.models import user as user_schema
from app.core import security
from app.api import deps

router = APIRouter()

@router.post("/register", response_model=user_schema.User)
def register(user_in: user_schema.UserCreate, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    
    user = UserModel(
        username=user_in.username,
        nickname=user_in.nickname,
        avatar=user_in.avatar,
        phone=user_in.phone,
        role_level=user_in.role_level if user_in.role_level is not None else 5,
        hashed_password=security.get_password_hash(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=user_schema.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(UserModel).filter(UserModel.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=400, detail="Incorrect username or password"
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token = security.create_access_token(subject=user.username)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=user_schema.User)
def read_users_me(current_user: UserModel = Depends(deps.get_current_user)):
    return current_user
