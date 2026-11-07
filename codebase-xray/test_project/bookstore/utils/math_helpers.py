def clamp(value, low, high):
    return max(low, min(value, high))


def factorial(n):
    # Only calls itself — nothing else uses it.
    return 1 if n <= 1 else n * factorial(n - 1)
