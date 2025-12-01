from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
import shutil
import os
import uuid
import random

from app.db.repository import get_db
from app.models.user import User as UserModel
from app.api.models import user as user_schema
from app.core import security
from app.api import deps

router = APIRouter()

def generate_random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

@router.post("/register", response_model=user_schema.User)
def register(user_in: user_schema.UserCreate, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    
    # Generate unique 6-digit number
    while True:
        number = random.randint(100000, 999999)
        if not db.query(UserModel).filter(UserModel.number == number).first():
            break

    user = UserModel(
        username=user_in.username,
        nickname=user_in.nickname,
        avatar=user_in.avatar,
        phone=user_in.phone,
        role_level=user_in.role_level if user_in.role_level is not None else 5,
        hashed_password=security.get_password_hash(user_in.password),
        chat_color=generate_random_color(),
        number=number
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

@router.put("/profile", response_model=user_schema.User)
def update_profile(
    user_in: user_schema.UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_active_user)
):
    current_user.nickname = user_in.nickname
    if user_in.avatar is not None:
        current_user.avatar = user_in.avatar
    if user_in.phone is not None:
        current_user.phone = user_in.phone
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/password", response_model=dict)
def update_password(
    password_in: user_schema.PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_active_user)
):
    if not security.verify_password(password_in.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    
    current_user.hashed_password = security.get_password_hash(password_in.new_password)
    db.commit()
    return {"message": "Password updated successfully"}

@router.post("/upload-avatar", response_model=dict)
def upload_avatar(
    file: UploadFile = File(...),
    current_user: UserModel = Depends(deps.get_current_active_user)
):
    # Ensure directory exists
    upload_dir = "/Users/edric/Desktop/react/tbnt-api/data/image"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Return relative URL (assuming static mount is /static)
    # Actually, we should return full URL or path. Frontend will prepend base URL.
    # Let's return just the filename or relative path.
    # Frontend can use http://localhost:8000/static/{filename}
    return {"url": f"/static/{filename}"}

