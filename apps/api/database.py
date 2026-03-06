import os
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.engine import make_url
from apps.api.settings import init_settings

init_settings()

DATABASE_WRITE_URL = os.getenv("DATABASE_WRITE_URL")
DATABASE_READ_URL = os.getenv("DATABASE_READ_URL")

if not DATABASE_WRITE_URL:
    raise ValueError("DATABASE_WRITE_URL environment variable not set")
if not DATABASE_READ_URL:
    raise ValueError("DATABASE_READ_URL environment variable not set")

write_engine = create_engine(DATABASE_WRITE_URL)
read_engine = create_engine(DATABASE_READ_URL)

logger = logging.getLogger("apps.api.database")


def _db_target(raw_url: str) -> str:
    u = make_url(raw_url)
    return f"{u.host}:{u.port}/{u.database}"


logger.info(
    f"DB routing configured | write={_db_target(DATABASE_WRITE_URL)} | read={_db_target(DATABASE_READ_URL)}"
)

SessionLocalWrite = sessionmaker(autocommit=False, autoflush=False, bind=write_engine)
SessionLocalRead = sessionmaker(autocommit=False, autoflush=False, bind=read_engine)


class Base(DeclarativeBase):
    pass


def get_write_db():
    db = SessionLocalWrite()
    try:
        yield db
    finally:
        db.close()


def get_read_db():
    db = SessionLocalRead()
    try:
        yield db
    finally:
        db.close()
