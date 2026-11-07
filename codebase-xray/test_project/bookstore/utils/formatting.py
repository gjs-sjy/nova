def format_price(amount):
    return f"${amount:.2f}"


def render_template(name, values):
    return f"[{name}] " + ", ".join(f"{k}={v}" for k, v in values.items())


def slugify(text):
    return text.lower().replace(" ", "-")
