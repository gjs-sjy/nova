from utils.email import send_email
from utils.formatting import render_template, format_price


def send_receipt(user_id, total):
    body = render_template("receipt", {"total": format_price(total)})
    send_email(user_id, "Your receipt", body)


def send_password_reset(user_id):
    # Planned feature, never called.
    send_email(user_id, "Reset your password", "...")
