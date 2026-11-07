from db.migrations import run_migrations
from db.repository import BookRepository
from db.models import Book


def seed_database():
    run_migrations()
    repo = BookRepository()
    for title, price in [("Dune", 12.5), ("SICP", 30.0)]:
        repo.save_book(Book(title, price))
