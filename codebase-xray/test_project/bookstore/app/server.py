from utils.logging_utils import log


class Router:
    def __init__(self):
        self.routes = {}

    def get(self, path):
        return self.register("GET", path)

    def post(self, path):
        return self.register("POST", path)

    def register(self, method, path):
        def decorator(func):
            self.routes[(method, path)] = func
            return func
        return decorator

    def run(self):
        log("server", f"starting with {len(self.routes)} routes")


app = Router()
router = app


def create_app(config):
    from app.routes import books, users, orders  # noqa: F401  (registers routes)
    log("server", f"port {config['port']}")
    return app
