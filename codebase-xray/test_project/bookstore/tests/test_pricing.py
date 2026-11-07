from services.pricing import apply_discount, add_tax


def test_discount():
    assert apply_discount(100, 2) == 90


def test_tax():
    assert add_tax(100) > 100
