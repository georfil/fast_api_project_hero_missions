from sqlmodel import create_engine, Session
from sqlmodel import SQLModel

from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from typing import Annotated


DATABASE_URL = "sqlite:///./hero_missions.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}) #check_same_thread is required for using sqlite with FastApi


def get_session():
    with Session(engine) as session:
        yield session

#Create alias for get_session dependency, to make it reusable
SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    SQLModel.metadata.create_all(engine)  # runs once when the server starts
    yield
    # --- SHUTDOWN ---
