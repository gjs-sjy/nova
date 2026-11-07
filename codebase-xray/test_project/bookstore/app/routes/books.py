from app.server import app
from services.book_service import BookService
from utils.validation import validate_book

service = BookService()


@app.get("/books")
def list_books():
    return service.list_all()


@app.post("/books")
def add_book(data):
    validate_book(data)
    return service.create(data)
