# Book Management REST API

## About
This is a small Flask API I built to practice backend development and RESTful design. It lets you add and view books using either a browser form or JSON endpoints. I wanted to learn how to build APIs and connect them to simple frontends.

## Motivation
I created this project to get hands-on experience with Flask, REST APIs, and basic HTML forms. It’s a fun way to manage a list of books and experiment with web development.

## Features
- Add books via browser form or JSON API
- List all books (HTML or JSON)
- Full CRUD: Get, Update, Delete individual books
- SQLite persistence (no data lost on restart)
- Simple HTML interface for quick testing

## How to Run
```powershell
pip install flask
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

## API Usage Examples

Add a book:
```powershell
Invoke-WebRequest -Uri http://localhost:5000/books -Method POST -ContentType "application/json" -Body '{"title":"Clean Code","author":"Robert Martin"}'
```

Get all books:
```powershell
Invoke-WebRequest -Uri http://localhost:5000/books
```

Update a book:
```powershell
Invoke-WebRequest -Uri http://localhost:5000/books/1 -Method PUT -ContentType "application/json" -Body '{"title":"Clean Code (Updated)"}'
```

Delete a book:
```powershell
Invoke-WebRequest -Uri http://localhost:5000/books/1 -Method DELETE
```

## Future Improvements
- Add user authentication and authorization
- Improve the HTML interface with edit/delete buttons
- Add search and filtering capabilities

Tip

- If port 5000 is busy, run: `set FLASK_RUN_PORT=5001; python app.py`
