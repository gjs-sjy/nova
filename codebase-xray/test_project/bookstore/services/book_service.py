from db.repository import BookRepository
from db.models import Book


class BookService:
    def __init__(self):
        self.repo = BookRepository()

    def list_all(self):
        return [book.to_dict() for book in self.repo.find_all()]

    def create(self, data):
        book = Book(data["title"], data["price"])
        self.repo.save_book(book)
        return book.to_dict()
