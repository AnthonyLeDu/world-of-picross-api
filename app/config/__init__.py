import os
from dotenv import load_dotenv

load_dotenv(override=True)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS").split(",")
DB_ECHO_LOG = True if os.getenv("DEBUG") == "True" else False

DATABASE_URL: str = (
    "postgresql://"\
    f"{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}"\
    f"@{os.getenv("POSTGRES_SERVER")}:{os.getenv("POSTGRES_PORT")}"\
    f"/{os.getenv("POSTGRES_DB")}"
)