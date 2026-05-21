from collections.abc import Sequence
from fastapi import APIRouter, HTTPException, status
from ..dependencies import CurrentUser, AdminUser, Pagination
from ..models import Hero, HeroCreate, HeroUpdate
from ..db import SessionDep
from sqlmodel import select

router = APIRouter(prefix="/heroes", tags=["Heroes"])


@router.get("", summary="List heroes", description="Returns a paginated list of all heroes.")
def get_heroes(pagination: Pagination, session: SessionDep) -> Sequence[Hero]:
    """Retrieve a paginated list of heroes.

    Args:
        pagination: Page number and page size query parameters.
        session: The database session dependency.

    Returns:
        A list of Hero objects for the requested page.
    """
    offset = pagination.page * pagination.size
    max_items = pagination.size
    return session.exec(select(Hero).limit(max_items).offset(offset=offset)).all()


@router.get("/{hero_id}", summary="Get hero", description="Returns a single hero by ID.")
def get_hero(hero_id: int, session:SessionDep) -> Hero:
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


@router.patch("/{hero_id}", summary="Update hero", description="Partially updates a hero. Only provided fields are applied.")
def update_hero(hero_id: int, data: HeroUpdate, _: CurrentUser, session: SessionDep) -> Hero:
    """Partially update a hero by ID.

    Args:
        hero_id: The unique integer ID of the hero to update.
        data: Fields to update, only provided fields are applied.
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


@router.post("", summary="Create hero", description="Creates a new hero. Requires authentication.")
def create_hero(data: HeroCreate, _: CurrentUser, session: SessionDep) -> Hero:
    """Create a new hero.

    Args:
        data: The fields required to create the hero.
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


@router.delete("/{hero_id}", summary="Delete hero", description="Deletes a hero by ID. Requires admin. Fails if the hero has active missions.")
def delete_hero(hero_id: int, _: AdminUser, session: SessionDep) -> Hero:
    """Delete a hero by ID.

    Args:
        hero_id: The unique integer ID of the hero to delete.
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
