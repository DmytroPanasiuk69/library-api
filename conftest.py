import os
import pytest
from app import create_app

TEST_DB_CONFIG = {
    "host": os.environ.get("POSTGRES_HOST", "localhost"),
    "dbname": os.environ.get("POSTGRES_DB", "library_test_db"),
    "user": os.environ.get("POSTGRES_USER", "postgres"),
    "password": os.environ.get("POSTGRES_PASSWORD", "secret"),
    "port": os.environ.get("POSTGRES_PORT", "5434")
}


@pytest.fixture(scope="session")
def app():

    app = create_app(TEST_DB_CONFIG)

    yield app


@pytest.fixture(scope="function")
def client(app):

    cur = app.conn.cursor()

    cur.execute("""
    TRUNCATE books, authors RESTART IDENTITY CASCADE
    """)

    return app.test_client()