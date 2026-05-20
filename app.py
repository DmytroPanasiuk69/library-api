from flask import Flask, request, jsonify
import psycopg2

DEFAULT_DB_CONFIG = {
    "host": "127.0.0.1",
    "dbname": "library_test_db",
    "user": "postgres",
    "password": "secret",
    "port": "5434"
}


def create_app(db_config=None):

    app = Flask(__name__)

    config = db_config or DEFAULT_DB_CONFIG

    conn = psycopg2.connect(**config)
    conn.autocommit = True

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS authors (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        birth_year INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        genre VARCHAR(255),
        year_published INTEGER,
        author_id INTEGER REFERENCES authors(id) ON DELETE SET NULL,
        created_by VARCHAR(255) NOT NULL
    )
    """)

    app.conn = conn

    # ---------------- AUTHORS ----------------

    @app.route('/api/authors', methods=['POST'])
    def create_author():

        data = request.json

        if data is None:
            return jsonify({
                "error": "JSON required"
            }), 400

        name = data.get("name")

        if not name:
            return jsonify({
                "error": "field 'name' is required"
            }), 400

        birth_year = data.get("birth_year")

        cur = app.conn.cursor()

        cur.execute("""
        INSERT INTO authors (name, birth_year)
        VALUES (%s, %s)
        RETURNING id, name, birth_year
        """, (name, birth_year))

        author = cur.fetchone()

        return jsonify({
            "id": author[0],
            "name": author[1],
            "birth_year": author[2]
        }), 201

    @app.route('/api/authors', methods=['GET'])
    def get_authors():

        cur = app.conn.cursor()

        cur.execute("""
        SELECT id, name, birth_year
        FROM authors
        ORDER BY id
        """)

        authors = cur.fetchall()

        result = []

        for author in authors:
            result.append({
                "id": author[0],
                "name": author[1],
                "birth_year": author[2]
            })

        return jsonify(result), 200

    @app.route('/api/authors/<int:author_id>', methods=['GET'])
    def get_author(author_id):

        cur = app.conn.cursor()

        cur.execute("""
        SELECT id, name, birth_year
        FROM authors
        WHERE id = %s
        """, (author_id,))

        author = cur.fetchone()

        if not author:
            return jsonify({
                "error": "Author not found"
            }), 404

        return jsonify({
            "id": author[0],
            "name": author[1],
            "birth_year": author[2]
        }), 200

    @app.route('/api/authors/<int:author_id>', methods=['DELETE'])
    def delete_author(author_id):

        cur = app.conn.cursor()

        cur.execute("""
        DELETE FROM authors
        WHERE id = %s
        RETURNING id
        """, (author_id,))

        deleted = cur.fetchone()

        if not deleted:
            return jsonify({
                "error": "Author not found"
            }), 404

        return '', 204

    @app.route('/api/authors/<int:author_id>/books', methods=['GET'])
    def get_author_books(author_id):

        cur = app.conn.cursor()

        cur.execute("""
        SELECT id FROM authors
        WHERE id = %s
        """, (author_id,))

        author = cur.fetchone()

        if not author:
            return jsonify({
                "error": "Author not found"
            }), 404

        cur.execute("""
        SELECT id, title, genre, year_published, author_id, created_by
        FROM books
        WHERE author_id = %s
        ORDER BY id
        """, (author_id,))

        books = cur.fetchall()

        result = []

        for book in books:
            result.append({
                "id": book[0],
                "title": book[1],
                "genre": book[2],
                "year_published": book[3],
                "author_id": book[4],
                "created_by": book[5]
            })

        return jsonify(result), 200

    # ---------------- BOOKS ----------------

    @app.route('/api/books', methods=['POST'])
    def create_book():

        data = request.json

        if data is None:
            return jsonify({
                "error": "JSON required"
            }), 400

        title = data.get("title")
        created_by = data.get("created_by")

        if not title:
            return jsonify({
                "error": "field 'title' is required"
            }), 400

        if not created_by:
            return jsonify({
                "error": "field 'created_by' is required"
            }), 400

        genre = data.get("genre")
        year_published = data.get("year_published")
        author_id = data.get("author_id")

        cur = app.conn.cursor()

        if author_id:

            cur.execute("""
            SELECT id FROM authors
            WHERE id = %s
            """, (author_id,))

            author = cur.fetchone()

            if not author:
                return jsonify({
                    "error": f"Author with id {author_id} not found"
                }), 400

        cur.execute("""
        INSERT INTO books
        (title, genre, year_published, author_id, created_by)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, title, genre, year_published, author_id, created_by
        """, (
            title,
            genre,
            year_published,
            author_id,
            created_by
        ))

        book = cur.fetchone()

        return jsonify({
            "id": book[0],
            "title": book[1],
            "genre": book[2],
            "year_published": book[3],
            "author_id": book[4],
            "created_by": book[5]
        }), 201

    @app.route('/api/books', methods=['GET'])
    def get_books():

        genre = request.args.get("genre")
        author_id = request.args.get("author_id")
        q = request.args.get("q")

        cur = app.conn.cursor()

        query = """
        SELECT id, title, genre, year_published, author_id, created_by
        FROM books
        WHERE 1=1
        """

        params = []

        if genre:
            query += " AND genre = %s"
            params.append(genre)

        if author_id:
            query += " AND author_id = %s"
            params.append(author_id)

        if q:
            query += " AND title ILIKE %s"
            params.append(f"%{q}%")

        query += " ORDER BY id"

        cur.execute(query, tuple(params))

        books = cur.fetchall()

        result = []

        for book in books:
            result.append({
                "id": book[0],
                "title": book[1],
                "genre": book[2],
                "year_published": book[3],
                "author_id": book[4],
                "created_by": book[5]
            })

        return jsonify(result), 200

    @app.route('/api/books/<int:book_id>', methods=['GET'])
    def get_book(book_id):

        cur = app.conn.cursor()

        cur.execute("""
        SELECT id, title, genre, year_published, author_id, created_by
        FROM books
        WHERE id = %s
        """, (book_id,))

        book = cur.fetchone()

        if not book:
            return jsonify({
                "error": "Book not found"
            }), 404

        return jsonify({
            "id": book[0],
            "title": book[1],
            "genre": book[2],
            "year_published": book[3],
            "author_id": book[4],
            "created_by": book[5]
        }), 200

    @app.route('/api/books/<int:book_id>', methods=['DELETE'])
    def delete_book(book_id):

        cur = app.conn.cursor()

        cur.execute("""
        DELETE FROM books
        WHERE id = %s
        RETURNING id
        """, (book_id,))

        deleted = cur.fetchone()

        if not deleted:
            return jsonify({
                "error": "Book not found"
            }), 404

        return '', 204

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)