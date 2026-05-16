from fastapi import APIRouter, HTTPException, status
from dependencies import CurrentUser, AdminUser
from models import Hero, HeroCreate, HeroUpdate
from db import SessionDep
from sqlmodel import select

router = APIRouter(prefix="/heroes", tags=["Heroes"])

@router.get("")
def get_heroes(session:SessionDep): #Add pagination later
    return session.exec(select(Hero)).all()

@router.get("/{hero_id}")
def get_hero(hero_id: int, session:SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(
            status_code=404,
            detail=f"No hero was found with this id: {hero_id}"
        )
    return hero

@router.patch("/{hero_id}")
def update_hero(hero_id: int, data: HeroUpdate, user: CurrentUser, session: SessionDep):

    # Fetch the hero based on the id
    hero = session.get(Hero, hero_id)

    #Check if it found heroes with this id
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hero was found with this id: {hero_id}"
        )
    
    #For the provided value only, update the hero
    for field, value in data.model_dump(exclude_unset=True).items():
        print(field)
        setattr(hero, field, value)

    #Update the db with the new hero
    session.add(hero)
    session.commit()
    session.refresh(hero)

    return hero


@router.post("")
def create_hero(data: HeroCreate, user: CurrentUser, session: SessionDep):
    hero = Hero(**data.model_dump())
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@router.delete("/{hero_id}")
def delet_hero(hero_id: int,  user: AdminUser, session: SessionDep):

    # Fetch the hero based on the id
    hero = session.get(Hero, hero_id)

    #Check if it found heroes with this id
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hero was found with this id: {hero_id}"
        )

    #Update the db with the new hero
    session.delete(hero)
    session.commit()
    session.refresh(hero)

    return hero