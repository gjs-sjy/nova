import re


def validate_book(data):
    if not data.get("title"):
        raise ValueError("title required")


def validate_email(email):
    if not re.match(r"[^@]+@[^@]+", email):
        raise ValueError("bad email")


def validate_card(card):
    if not luhn_check(card):
        raise ValueError("bad card")


def luhn_check(number):
    digits = [int(d) for d in number if d.isdigit()]
    return len(digits) >= 12
