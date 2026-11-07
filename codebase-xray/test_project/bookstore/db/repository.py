from db.connection import get_connection


class BookRepository:
    def find_all(self):
        return self.execute("books")

    def save_book(self, book):
        self.execute("books").append(book)

    def execute(self, table):
        return get_connection()["tables"].setdefault(table, [])


class UserRepository:
    def find_by_id(self, user_id):
        return None

    def find_by_email(self, email):
        return None
