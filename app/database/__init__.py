from ..config import DATABASE_URL, DB_ECHO_LOG
from sqlmodel import SQLModel, create_engine
from ..models import *


engine = create_engine(
    url=DATABASE_URL,
    echo=DB_ECHO_LOG,
)


def init_db():
    SQLModel.metadata.create_all(engine)
