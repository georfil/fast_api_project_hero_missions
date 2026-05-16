from sqlmodel import Field, SQLModel, Relationship
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field as PydanticField


class StrictModel:
    model_config = ConfigDict(extra="forbid") #Prevent User from mispelling fields  

# ------------------------------------------------------------------------
# User Model
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    is_admin: bool = False

# User Schemas
class UserRegister(BaseModel):
    username: str 
    password : str

# ------------------------------------------------------------------------

# ------------------------------------------------------------------------
# Hero Model
class Hero(SQLModel, table=True):

    __tablename__ = "heroes"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    power: str 
    level: int
    active: bool

#Hero Schemas
hero_name = Annotated[str, PydanticField(min_length=3)]
hero_power = Annotated[str, PydanticField(min_length=3)]
hero_level = Annotated[int, PydanticField(ge=1, le=100)]

class HeroCreate(BaseModel, StrictModel):
    name: hero_name
    power: hero_power
    level: hero_level = 1
    active: bool = True


class HeroUpdate(BaseModel, StrictModel): #All args are optional
    name: hero_name | None = None
    power: hero_power | None = None
    level: hero_level | None = None
    active: bool | None = None
    model_config = ConfigDict(extra="forbid") #Prevent User from mispelling fields  

# ------------------------------------------------------------------------



# ------------------------------------------------------------------------
# Mission Model
class Mission(SQLModel, table=True):
    __tablename__ = "missions"

    id: int | None = Field(default=None, primary_key=True)
    title: str
    difficulty: int
    completed: bool
    hero_id: int = Field(foreign_key="heroes.id")
    hero: Hero | None = Relationship(back_populates="missions")

# Mission Schemas

mission_title = Annotated[str, PydanticField(min_length=5)]
mission_difficulty = Annotated[str, PydanticField(ge=1, le=10)]

class MissionCreate(BaseModel, StrictModel):
    title: mission_title
    difficulty: mission_difficulty
    completed: bool = False
    hero_id: int

class MissionUpdate(BaseModel, StrictModel):
    title: mission_title | None = None
    difficulty: mission_difficulty | None = None
    completed: bool | None = None
    hero_id: int | None = None
