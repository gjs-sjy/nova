import pytest
from db.models import Book


@pytest.fixture
def sample_book():
    return Book("Test", 1.0)
