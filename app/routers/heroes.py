from fastapi import APIRouter, HTTPException, status
from ..dependencies import CurrentUser, AdminUser
from ..models import Hero, HeroCreate, HeroUpdate
from ..db import SessionDep
from sqlmodel import select

router = APIRouter(prefix="/heroes", tags=["Heroes"])

@router.get("")
def get_heroes(session:SessionDep): #Add pagination later
    """Retrieve all heroes.

    Args:
        session: The database session dependency.

    Returns:
        A list of all Hero objects.
    """

    return session.exec(select(Hero)).all()


@router.get("/{hero_id}")
def get_hero(hero_id: int, session:SessionDep):
    """Retrieve a single hero by ID.

    Args:
        hero_id: The unique integer ID of the hero to retrieve.
        session: The database session dependency.

    Returns:
        The Hero object matching the given ID.

    Raises:
        HTTPException: 404 if no hero exists with the given ID.
    """

    hero = session.get(Hero, hero_id)

    if not hero:
        raise HTTPException(
            status_code=404,
            detail=f"No hero was found with this id: {hero_id}"
        )
    
    return hero


@router.patch("/{hero_id}")
def update_hero(hero_id: int, data: HeroUpdate, user: CurrentUser, session: SessionDep):
    """Partially update a hero by ID.

    Args:
        hero_id: The unique integer ID of the hero to update.
        data: Fields to update, only provided fields are applied.
        user: The authenticated user making the request.
        session: The database session dependency.

    Returns:
        The updated Hero object.

    Raises:
        HTTPException: 404 if no hero exists with the given ID.
    """

    # Fetch the hero based on the id
    hero = session.get(Hero, hero_id)

    #Check if it found a hero with this id
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hero was found with this id: {hero_id}"
        )
    
    #For the provided values only, update the hero
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(hero, field, value)

    #Update the db with the new hero
    session.add(hero)
    session.commit()
    session.refresh(hero)

    return hero


@router.post("")
def create_hero(data: HeroCreate, user: CurrentUser, session: SessionDep):
    """Create a new hero.

    Args:
        data: The fields required to create the hero.
        user: The authenticated user making the request.
        session: The database session dependency.

    Returns:
        The newly created Hero object.
    """
    # Initiatialise Hero Object
    hero = Hero(**data.model_dump())

    #Update DB
    session.add(hero)
    session.commit()
    session.refresh(hero)

    return hero


@router.delete("/{hero_id}")
def delet_hero(hero_id: int,  user: AdminUser, session: SessionDep):
    """Delete a hero by ID.

    Args:
        hero_id: The unique integer ID of the hero to delete.
        user: The authenticated admin user making the request.
        session: The database session dependency.

    Returns:
        The deleted Hero object.

    Raises:
        HTTPException: 404 if no hero exists with the given ID.
        HTTPException: 409 if the hero has one or more active missions.
    """
    # Fetch the hero based on the id
    hero = session.get(Hero, hero_id)

    #Check if it found heroes with this id
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hero was found with this id: {hero_id}"
        )
    
    # Check if hero has at least one active mission
    active_missions = [mission for mission in hero.missions if not mission.completed]
    if active_missions: 
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Can't delete hero with active missions."
        )
        
    #Update the db with the new hero
    session.delete(hero)
    session.commit()

    return hero