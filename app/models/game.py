from sqlmodel import Field, SQLModel
from sqlalchemy import Column, ARRAY, BOOLEAN


class Game(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    difficulty: int
    content: list[list[bool]] | None = Field(
        default=None,
        sa_column=Column(ARRAY(BOOLEAN)),
    )
