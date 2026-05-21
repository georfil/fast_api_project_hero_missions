from fastapi import APIRouter, HTTPException, status
from ..dependencies import CurrentUser, AdminUser
from ..models import Mission, MissionCreate, MissionUpdate, Hero
from ..db import SessionDep
from sqlmodel import select

router = APIRouter(prefix="/missions", tags=["Missions"])

@router.get("")
def get_missions(session:SessionDep): #Add pagination later
    """Retrieve all missions.

    Args:
        session: The database session dependency.

    Returns:
        A list of all Mission objects.
    """
    return session.exec(select(Mission)).all()


@router.get("/{mission_id}")
def get_mission(mission_id: int, session:SessionDep):
    """Retrieve a single mission by ID.

    Args:
        mission_id: The unique integer ID of the mission to retrieve.
        session: The database session dependency.

    Returns:
        The Mission object matching the given ID.

    Raises:
        HTTPException: 404 if no mission exists with the given ID.
    """

    mission = session.get(Mission, mission_id)

    if not mission:
        raise HTTPException(
            status_code=404,
            detail=f"No mission was found with this id: {mission_id}"
        )
    
    return mission

@router.patch("/{mission_id}")
def update_mission(mission_id: int, data: MissionUpdate, user: CurrentUser, session: SessionDep):
    """Partially update a mission by ID.

    Args:
        mission_id: The unique integer ID of the mission to update.
        data: Fields to update; only provided fields are applied.
        user: The authenticated user making the request.
        session: The database session dependency.

    Returns:
        The updated Mission object.

    Raises:
        HTTPException: 404 if no mission exists with the given ID.
    """

    # Fetch the mission based on the id
    mission = session.get(Mission, mission_id)

    #Check if it found missions with this id
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No mission was found with this id: {mission_id}"
        )
    
    #For the provided value only, update the hero
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(mission, field, value)

    #Update the db with the new hero
    session.add(mission)
    session.commit()
    session.refresh(mission)

    return mission


@router.post("")
def create_mission(data: MissionCreate, user: CurrentUser, session: SessionDep):
    """Create a new mission.

    Args:
        data: The fields required to create the mission.
        user: The authenticated user making the request.
        session: The database session dependency.

    Returns:
        The newly created Mission object.

    Raises:
        HTTPException: 409 if the referenced hero does not exist.
    """
    # Initiatialise Mission Object
    mission = Mission(**data.model_dump())

    # Check if hero exists
    hero_id = mission.hero_id
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail= f"Hero with id = {hero_id} doesn't exist. Can't create mission"
        )

    # Update DB
    session.add(mission)
    session.commit()
    session.refresh(mission)

    return mission


@router.delete("/{mission_id}")
def delete_mission(mission_id: int,  user: AdminUser, session: SessionDep):
    """Delete a mission by ID.

    Args:
        mission_id: The unique integer ID of the mission to delete.
        user: The authenticated admin user making the request.
        session: The database session dependency.

    Returns:
        The deleted Mission object.

    Raises:
        HTTPException: 404 if no mission exists with the given ID.
    """
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

    return mission