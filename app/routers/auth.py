from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from models import UserRegister, User
from db import SessionDep
from sqlmodel import select
from security import hash_password, verify_password
from dependencies import CurrentUser
from security import create_jwt_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register_user(data: UserRegister, session: SessionDep ):
    
    username = data.username.strip().lower() 

    #Check is user already exists
    existing = session.exec(select(User).where(User.username == username))
    if existing:
        pass # raise error - user already exists
    
    #Hash User's password
    raw_password = data.password
    hashed_password = hash_password(raw_password)

    #Create User
    user = User(
        username=username,
        hashed_password=hashed_password,
        is_admin=False
    )

    #Add User to db
    session.add(user)
    session.commit()
    session.refresh(user)

    return user

@router.post("/login")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()] ,session: SessionDep):
    
    #Check password
    user = session.exec(select(User).where(User.username == form.username)).first()

    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "access_token": create_jwt_token(user.username),
        "token_type" : "bearer"
    }

@router.get("/me")
def me(user: CurrentUser):
    return {
        "username":user.username,
        "admin":user.is_admin
    }