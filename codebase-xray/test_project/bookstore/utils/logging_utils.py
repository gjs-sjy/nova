import datetime


def log(source, message):
    print(f"{timestamp()} [{source}] {message}")


def timestamp():
    return datetime.datetime.now().isoformat(timespec="seconds")
