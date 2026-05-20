import pytest
from app import create_app

TEST_DB_CONFIG = {
    "host": "127.0.0.1",
    "dbname": "library_test_db",
    "user": "postgres",
    "password": "secret",
    "port": "5434"
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
