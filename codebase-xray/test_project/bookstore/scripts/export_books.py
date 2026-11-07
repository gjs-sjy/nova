import json
from db.repository import BookRepository


def export(path):
    books = BookRepository().find_all()
    with open(path, "w") as f:
        json.dump([b.title for b in books], f)


if __name__ == "__main__":
    export("books.json")
