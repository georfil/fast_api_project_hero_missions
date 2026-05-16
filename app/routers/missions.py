from fastapi import APIRouter, HTTPException, status
from dependencies import CurrentUser, AdminUser
from models import Mission, MissionCreate, MissionUpdate
from db import SessionDep
from sqlmodel import select

router = APIRouter(prefix="/missions", tags=["Missions"])

@router.get("")
def get_missions(session:SessionDep): #Add pagination later
    return session.exec(select(Mission)).all()

@router.get("/{mission_id}")
def get_mission(mission_id: int, session:SessionDep):
    hero = session.get(Mission, mission_id)
    if not hero:
        raise HTTPException(
            status_code=404,
            detail=f"No mission was found with this id: {mission_id}"
        )
    return hero

@router.patch("/{mission_id}")
def update_mission(mission_id: int, data: MissionUpdate, user: CurrentUser, session: SessionDep):

    # Fetch the hero based on the id
    mission = session.get(Mission, mission_id)

    #Check if it found heroes with this id
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No mission was found with this id: {mission_id}"
        )
    
    #For the provided value only, update the hero
    for field, value in data.model_dump(exclude_unset=True).items():
        print(field)
        setattr(mission, field, value)

    #Update the db with the new hero
    session.add(mission)
    session.commit()
    session.refresh(mission)

    return mission


@router.post("")
def create_hero(data: MissionCreate, user: CurrentUser, session: SessionDep):
    mission = Mission(**data.model_dump())
    session.add(mission)
    session.commit()
    session.refresh(mission)
    return mission


@router.delete("/{hero_id}")
def delet_hero(mission_id: int,  user: AdminUser, session: SessionDep):

    # Fetch the hero based on the id
    mission = session.get(Mission, mission_id)

    #Check if it found heroes with this id
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No mission was found with this id: {mission_id}"
        )

    #Update the db with the new hero
    session.delete(mission)
    session.commit()
    session.refresh(mission)

    return mission