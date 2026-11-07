# This file has its own log() — so does utils/logging_utils.py.
EVENTS = []


def log(message):
    EVENTS.append(message)


def record_event(name, user_id):
    log(f"{name} by {user_id}")
