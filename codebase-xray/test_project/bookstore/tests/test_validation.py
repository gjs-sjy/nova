import pytest
from utils.validation import validate_email


def test_bad_email():
    with pytest.raises(ValueError):
        validate_email("nope")
