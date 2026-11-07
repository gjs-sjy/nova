from config import DEFAULTS
from utils.math_helpers import clamp

PRICES = {1: 12.5, 2: 30.0, 3: 8.0}


def calculate_order_total(book_ids):
    subtotal = sum(PRICES.get(i, 0) for i in book_ids)
    subtotal = apply_discount(subtotal, len(book_ids))
    return round_money(add_tax(subtotal))


def apply_discount(amount, item_count):
    percent = clamp(item_count * 5, 0, 20)
    return amount * (1 - percent / 100)


def add_tax(amount):
    return amount * (1 + DEFAULTS["tax_rate"])


def round_money(amount):
    return round(amount, 2)
