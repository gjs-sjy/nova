from app.server import app
from services.user_service import UserService, authenticate

users = UserService()


@app.get("/users/{user_id}")
def get_user_route(user_id):
    return users.get(user_id)


@app.post("/register")
def register_route(data):
    return users.register(data["email"], data["password"])


@app.post("/login")
def login_route(data):
    return authenticate(data["email"], data["password"])
