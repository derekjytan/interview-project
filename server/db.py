import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = os.environ["DATABASE_URL"]

# Compose and database clients use standard Postgres URLs. Select Psycopg 3
# explicitly for SQLAlchemy rather than its default PostgreSQL driver.
database_url = make_url(DATABASE_URL).set(drivername="postgresql+psycopg")
engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    # Services commit successful writes before returning. Closing the session
    # rolls back unfinished work, including when a request raises an exception.
    with SessionLocal() as session:
        yield session
