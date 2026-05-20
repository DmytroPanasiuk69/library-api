class TestAuthors:

    def test_get_authors_empty(self, client):

        response = client.get("/api/authors")

        assert response.status_code == 200
        assert response.get_json() == []

    def test_create_author(self, client):

        response = client.post("/api/authors", json={
            "name": "Taras Shevchenko",
            "birth_year": 1814
        })

        assert response.status_code == 201

        data = response.get_json()

        assert data["name"] == "Taras Shevchenko"
        assert data["birth_year"] == 1814
        assert "id" in data

    def test_create_author_without_name(self, client):

        response = client.post("/api/authors", json={})

        assert response.status_code == 400

    def test_get_author_by_id(self, client):

        author = client.post("/api/authors", json={
            "name": "Lesya Ukrainka"
        }).get_json()

        response = client.get(f"/api/authors/{author['id']}")

        assert response.status_code == 200

    def test_get_author_not_found(self, client):

        response = client.get("/api/authors/999")

        assert response.status_code == 404

    def test_delete_author(self, client):

        author = client.post("/api/authors", json={
            "name": "Ivan Franko"
        }).get_json()

        response = client.delete(f"/api/authors/{author['id']}")

        assert response.status_code == 204

    def test_delete_author_not_found(self, client):

        response = client.delete("/api/authors/999")

        assert response.status_code == 404

    def test_get_author_books(self, client):
        author = client.post("/api/authors", json={
            "name": "Іван Франко",
            "birth_year": 1856
        }).get_json()

        client.post("/api/books", json={
            "title": "Zakhar Berkut",
            "author_id": author["id"],
            "created_by": "Дмитро Панасюк"
        })

        response = client.get(f"/api/authors/{author['id']}/books")

        assert response.status_code == 200

        data = response.get_json()

        assert len(data) == 1
        assert data[0]["title"] == "Zakhar Berkut"

    def test_get_author_books_empty(self, client):
        author = client.post("/api/authors", json={
            "name": "Леся Українка"
        }).get_json()

        response = client.get(f"/api/authors/{author['id']}/books")

        assert response.status_code == 200
        assert response.get_json() == []

    def test_get_author_books_not_found(self, client):
        response = client.get("/api/authors/999/books")

        assert response.status_code == 404

    def test_delete_author_keeps_books(self, client):
        author = client.post("/api/authors", json={
            "name": "Іван Франко"
        }).get_json()

        book = client.post("/api/books", json={
            "title": "Zakhar Berkut",
            "author_id": author["id"],
            "created_by": "Дмитро Панасюк"
        }).get_json()

        delete_response = client.delete(f"/api/authors/{author['id']}")

        assert delete_response.status_code == 204

        response = client.get(f"/api/books/{book['id']}")

        assert response.status_code == 200
        assert response.get_json()["author_id"] is None
