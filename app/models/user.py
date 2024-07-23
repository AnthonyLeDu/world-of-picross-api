from sqlmodel import Field, SQLModel, Relationship


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    pseudo: str = Field(unique=True)
    email: str = Field(unique=True)
    password: str
    games: list["Game"] = Relationship(back_populates="creator")
