from utils.security import hash_password


class Book:
    def __init__(self, title, price):
        self.title = title
        self.price = price

    def to_dict(self):
        return {"title": self.title, "price": self.price}


class User:
    def __init__(self, email, password_hash):
        self.email = email
        self.password_hash = password_hash

    def to_dict(self):
        return {"email": self.email}

    def check_password(self, password):
        return hash_password(password) == self.password_hash
