import pytest
from fastapi.testclient import TestClient

from app import models  # noqa: F401 — register tables on Base.metadata
from app.database import Base, configure_database, get_db


@pytest.fixture()
def db_url(tmp_path):
    return f"sqlite:///{tmp_path / 'tasks.db'}"


@pytest.fixture()
def db_engine(db_url):
    configure_database(db_url)
    from app import database

    Base.metadata.create_all(bind=database.engine)
    yield database.engine
    Base.metadata.drop_all(bind=database.engine)
    database.engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    from app.database import SessionLocal

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_engine):
    from app.database import SessionLocal
    from app.main import app

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
