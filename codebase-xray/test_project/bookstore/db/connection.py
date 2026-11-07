_connection = None


def get_connection():
    global _connection
    if _connection is None:
        _connection = {"tables": {}}
    return _connection


def close_connection():
    global _connection
    _connection = None
