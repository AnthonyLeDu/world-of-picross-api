from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..models.user import User
from ..models.game import Game
from sqlmodel import Session, select
from ..database import engine

router = APIRouter()


class LoginData(BaseModel):
    email: str
    password: str


@router.get("/users")
async def get_all_users():
    with Session(engine) as session:
        users = session.exec(select(User)).all()
    return users


@router.get("/user/{id}")
async def get_user(id: int):
    with Session(engine) as session:
        user = session.get(User, id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User does not exist.",
        )
    return user


@router.get("/user/{id}/games")
async def get_user_games(id: int):
    with Session(engine) as session:
        games = session.select(Game).where(Game.creator_id == id).all()
    return games


@router.post("/user")
async def create_user(user: User):
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


@router.put("/user/{id}")
async def update_user(id: int, user: User):
    # Be careful, all user fields must be provided otherwise default
    # ones will be used.
    # See https://fastapi.tiangolo.com/tutorial/body-updates/
    with Session(engine) as session:
        db_user = session.get(User, id)
        if db_user is None:
            raise HTTPException(
                status_code=404,
                detail="User does not exist.",
            )
        db_user.pseudo = user.pseudo
        db_user.email = user.email
        # TODO: Hash password
        # (see https://sqlmodel.tiangolo.com/tutorial/fastapi/update-extra-data/)
        db_user.password = user.password
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    return db_user


@router.delete("/user/{id}")
async def delete_user(id: int):
    with Session(engine) as session:
        user = session.get(User, id)
        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User does not exist.",
            )
        session.delete(user)
        session.commit()
        # TODO: Return deleted response code


@router.post("/user/login")
async def log_user_in(login_data: LoginData):
    with Session(engine) as session:
        statement = (
            select(User)
            .where(User.email == login_data.email)
            .where(User.password == login_data.password)
        )
        user = session.exec(statement).one_or_none()
        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User does not exist or invalid credentials provided.",
            )
        return user
