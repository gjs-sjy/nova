from utils.logging_utils import log


def send_email(to, subject, body):
    log("email", f"to={to} subject={subject}")
    return True
