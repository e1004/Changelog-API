import pytest

from e1004.changelog_api.error import VersionNumberInvalidError
from e1004.changelog_api.service import validate_version_number


def test_it_raises_error_for_invalid_version_number():
    # given
    number = "1.0."

    # then
    with pytest.raises(VersionNumberInvalidError):
        # when
        validate_version_number(number)


def test_it_returns_valid_version_number():
    # given
    number = "1.0.1"
    # when
    result = validate_version_number(number)
    # then
    assert result == number
