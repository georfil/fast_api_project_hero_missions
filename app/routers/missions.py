from collections.abc import Sequence
from fastapi import APIRouter, HTTPException, status
from ..dependencies import CurrentUser, AdminUser, Pagination
from ..models import Mission, MissionCreate, MissionUpdate, Hero
from ..db import SessionDep
from sqlmodel import select

router = APIRouter(prefix="/missions", tags=["Missions"])


@router.get("", summary="List missions", description="Returns a paginated list of all missions.")
def get_missions(pagination: Pagination, session: SessionDep) -> Sequence[Mission]:
    """Retrieve a paginated list of missions.

    Args:
        pagination: Page number and page size query parameters.
        session: The database session dependency.

    Returns:
        A list of Mission objects for the requested page.
    """
    offset = pagination.page * pagination.size
    return session.exec(select(Mission).limit(pagination.size).offset(offset)).all()


@router.get("/{mission_id}", summary="Get mission", description="Returns a single mission by ID.")
def get_mission(mission_id: int, session:SessionDep) -> Mission:
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


@router.patch("/{mission_id}", summary="Update mission", description="Partially updates a mission. Only provided fields are applied.")
def update_mission(mission_id: int, data: MissionUpdate, _: CurrentUser, session: SessionDep) -> Mission:
    """Partially update a mission by ID.

    Args:
        mission_id: The unique integer ID of the mission to update.
        data: Fields to update; only provided fields are applied.
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

    #For the provided value only, update the mission
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(mission, field, value)

    #Update the db with the new mission
    session.add(mission)
    session.commit()
    session.refresh(mission)

    return mission


@router.post("", summary="Create mission", description="Creates a new mission assigned to an existing hero. Requires authentication.")
def create_mission(data: MissionCreate, _: CurrentUser, session: SessionDep) -> Mission:
    """Create a new mission.

    Args:
        data: The fields required to create the mission.
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
            detail=f"Hero with id = {hero_id} doesn't exist. Can't create mission"
        )

    # Update DB
    session.add(mission)
    session.commit()
    session.refresh(mission)

    return mission


@router.delete("/{mission_id}", summary="Delete mission", description="Deletes a mission by ID. Requires admin.")
def delete_mission(mission_id: int, _: AdminUser, session: SessionDep) -> Mission:
    """Delete a mission by ID.

    Args:
        mission_id: The unique integer ID of the mission to delete.
        session: The database session dependency.

    Returns:
        The deleted Mission object.

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

    #Update the db
    session.delete(mission)
    session.commit()

    return mission
