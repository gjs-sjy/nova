from config import load_config
from app.server import create_app
from db.seed import seed_database


def main():
    config = load_config()
    seed_database()
    app = create_app(config)
    app.run()


if __name__ == "__main__":
    main()
