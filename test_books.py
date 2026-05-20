class TestBooks:
    def test_get_books_empty(self, client):
        response = client.get("/api/books")

        assert response.status_code == 200
        assert response.get_json() == []

    def test_create_book(self, client):
        response = client.post("/api/books", json={
            "title": "Kobzar",
            "genre": "poetry",
            "year_published": 1840,
            "created_by": "Дмитро Панасюк"
        })

        assert response.status_code == 201
        data = response.get_json()

        assert data["title"] == "Kobzar"
        assert data["genre"] == "poetry"
        assert data["year_published"] == 1840
        assert data["created_by"] == "Дмитро Панасюк"
        assert "id" in data

    def test_create_book_without_title(self, client):
        response = client.post("/api/books", json={
            "genre": "poetry",
            "created_by": "Дмитро Панасюк"
        })

        assert response.status_code == 400

    def test_create_book_without_created_by(self, client):
        response = client.post("/api/books", json={
            "title": "Kobzar"
        })

        assert response.status_code == 400

    def test_create_book_with_author(self, client):
        author = client.post("/api/authors", json={
            "name": "Леся Українка",
            "birth_year": 1871
        }).get_json()

        response = client.post("/api/books", json={
            "title": "Lisova Pisnia",
            "genre": "drama",
            "year_published": 1911,
            "author_id": author["id"],
            "created_by": "Дмитро Панасюк"
        })

        assert response.status_code == 201

        data = response.get_json()

        assert data["author_id"] == author["id"]
        assert data["created_by"] == "Дмитро Панасюк"

    def test_create_book_with_nonexistent_author(self, client):
        response = client.post("/api/books", json={
            "title": "Test Book",
            "author_id": 999,
            "created_by": "Дмитро Панасюк"
        })

        assert response.status_code == 400

    def test_get_book_by_id(self, client):
        book = client.post("/api/books", json={
            "title": "Kobzar",
            "created_by": "Дмитро Панасюк"
        }).get_json()

        response = client.get(f"/api/books/{book['id']}")

        assert response.status_code == 200
        assert response.get_json()["title"] == "Kobzar"

    def test_get_book_not_found(self, client):
        response = client.get("/api/books/999")

        assert response.status_code == 404

    def test_delete_book(self, client):
        book = client.post("/api/books", json={
            "title": "Kobzar",
            "created_by": "Дмитро Панасюк"
        }).get_json()

        response = client.delete(f"/api/books/{book['id']}")

        assert response.status_code == 204

        check = client.get(f"/api/books/{book['id']}")
        assert check.status_code == 404


class TestBooksFilter:
    def test_filter_by_genre(self, client):
        client.post("/api/books", json={
            "title": "Kobzar",
            "genre": "poetry",
            "created_by": "Дмитро Панасюк"
        })

        client.post("/api/books", json={
            "title": "Tygrolovy",
            "genre": "novel",
            "created_by": "Дмитро Панасюк"
        })

        response = client.get("/api/books?genre=poetry")

        data = response.get_json()

        assert len(data) == 1
        assert data[0]["title"] == "Kobzar"

    def test_filter_by_author_id(self, client):
        author = client.post("/api/authors", json={
            "name": "Іван Франко"
        }).get_json()

        client.post("/api/books", json={
            "title": "Zakhar Berkut",
            "author_id": author["id"],
            "created_by": "Дмитро Панасюк"
        })

        client.post("/api/books", json={
            "title": "Kobzar",
            "created_by": "Дмитро Панасюк"
        })

        response = client.get(f"/api/books?author_id={author['id']}")

        data = response.get_json()

        assert len(data) == 1
        assert data[0]["title"] == "Zakhar Berkut"

    def test_search_by_title(self, client):
        client.post("/api/books", json={
            "title": "Kobzar",
            "created_by": "Дмитро Панасюк"
        })

        response = client.get("/api/books?q=kob")

        data = response.get_json()

        assert len(data) == 1
        assert data[0]["title"] == "Kobzar"

    def test_filter_no_results(self, client):
        response = client.get("/api/books?genre=horror")

        assert response.status_code == 200
        assert response.get_json() == []
