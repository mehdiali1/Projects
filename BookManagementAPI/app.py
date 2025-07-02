
# Book Management API
# Author: Mehdi Ahsan
# This is a simple Flask app I built to practice REST APIs and basic HTML forms.
# Now uses SQLite for persistence and includes basic CRUD.

from flask import Flask, request, jsonify, redirect, url_for
import os
import sqlite3

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "books.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL
            )
            """
        )

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def row_to_dict(row):
    return {"id": row["id"], "title": row["title"], "author": row["author"]}

@app.route('/')
def home():
    # Homepage with a form to add books and a link to view all
    return '''
    <h2>Book Management API</h2>
    <p>This is a personal project to learn Flask and REST API design.</p>
    <form action="/books" method="post">
      <label>Title: <input name="title" required></label><br>
      <label>Author: <input name="author" required></label><br>
      <button type="submit">Add Book</button>
    </form>
    <a href="/books/html">View Books (HTML)</a>
    '''

@app.route('/books', methods=['POST'])
def add_book():
    # Accept both form and JSON submissions
    title = request.form.get('title') or (request.get_json(silent=True) or {}).get('title')
    author = request.form.get('author') or (request.get_json(silent=True) or {}).get('author')
    if not title or not author:
        # Return error if missing fields
        return jsonify({'error': 'Title and author are required'}), 400
    with get_db() as conn:
        cur = conn.execute("INSERT INTO books(title, author) VALUES(?, ?)", (title.strip(), author.strip()))
        book_id = cur.lastrowid
        book = {"id": book_id, "title": title.strip(), "author": author.strip()}
    # Redirect to HTML list if submitted via form
    if request.form:
        return redirect(url_for('list_books_html'))
    return jsonify(book), 201

@app.route('/books', methods=['GET'])
def get_books():
    # Return all books as JSON
    with get_db() as conn:
        rows = conn.execute("SELECT id, title, author FROM books ORDER BY id DESC").fetchall()
        return jsonify([row_to_dict(r) for r in rows])

@app.route('/books/html')
def list_books_html():
    # Show all books in a simple HTML list
    with get_db() as conn:
        rows = conn.execute("SELECT id, title, author FROM books ORDER BY id DESC").fetchall()
        items = ''.join(f"<li>#{r['id']}: {r['title']} — {r['author']}</li>" for r in rows)
    return f"""
    <h3>Books</h3>
    <ul>{items or '<li>No books yet.</li>'}</ul>
    <a href='/'>Back</a>
    """

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    with get_db() as conn:
        row = conn.execute("SELECT id, title, author FROM books WHERE id=?", (book_id,)).fetchone()
        if not row:
            return jsonify({"error": "Book not found"}), 404
        return jsonify(row_to_dict(row))

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    author = (data.get('author') or '').strip()
    if not title and not author:
        return jsonify({"error": "Nothing to update"}), 400
    with get_db() as conn:
        row = conn.execute("SELECT id, title, author FROM books WHERE id=?", (book_id,)).fetchone()
        if not row:
            return jsonify({"error": "Book not found"}), 404
        new_title = title or row["title"]
        new_author = author or row["author"]
        conn.execute("UPDATE books SET title=?, author=? WHERE id=?", (new_title, new_author, book_id))
        return jsonify({"id": book_id, "title": new_title, "author": new_author})

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    with get_db() as conn:
        row = conn.execute("SELECT id FROM books WHERE id=?", (book_id,)).fetchone()
        if not row:
            return jsonify({"error": "Book not found"}), 404
        conn.execute("DELETE FROM books WHERE id=?", (book_id,))
        return jsonify({"message": "deleted", "id": book_id})

if __name__ == '__main__':
    # Run the app in debug mode for development
    init_db()
    app.run(debug=True)
