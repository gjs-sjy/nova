from db.repository import UserRepository
from db.models import User
from utils.security import hash_password, generate_token
from utils.validation import validate_email


class UserService:
    def __init__(self):
        self.repo = UserRepository()

    def get(self, user_id):
        return self.repo.find_by_id(user_id)

    def register(self, email, password):
        validate_email(email)
        user = User(email, hash_password(password))
        return user


def authenticate(email, password):
    user = UserRepository().find_by_email(email)
    if user and user.check_password(password):
        return generate_token(user.email)
    return None
