from fastapi import FastAPI
from .routers import auth, heroes, missions
from .db import lifespan

app = FastAPI(
    title="Secure Hero Missions",
    version="1.0.0",
    lifespan=lifespan 
)

app.include_router(auth.router)
app.include_router(heroes.router)
app.include_router(missions.router)

