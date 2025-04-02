import pytest
import os
import json
from core.profile import UserProfile

def test_profile_creation(tmp_path):
    profile_path = tmp_path / "test_profile.json"
    profile = UserProfile(str(profile_path))
    assert profile.data["name"] == ""
    profile.set_profile("TestUser", "", str(tmp_path))
    assert profile.data["name"] == "TestUser"
    profile.set_default_resolution("1080p")
    assert profile.get_default_resolution() == "1080p"