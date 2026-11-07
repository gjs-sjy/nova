from db.connection import get_connection


def run_migrations():
    migrate_v1()
    migrate_v2()


def migrate_v1():
    get_connection()["tables"]["books"] = []


def migrate_v2():
    get_connection()["tables"]["users"] = []
