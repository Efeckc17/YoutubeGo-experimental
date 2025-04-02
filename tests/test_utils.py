import pytest
from core.utils import format_time

def test_format_time():
    assert format_time(65000) == "01:05"
    assert format_time(3605000) == "01:00:05"