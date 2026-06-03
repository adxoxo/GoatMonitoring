"""Tests for the custom User model (admin accounts).

Workers are unauthenticated (see CLAUDE.md); this User model is for admin /
office-manager accounts that log in to the dashboard via JWT.
"""

import pytest
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db

User = get_user_model()


def test_project_uses_custom_user_model():
    assert User.__module__ == "apps.users.models"
    assert User.__name__ == "User"


def test_create_user():
    user = User.objects.create_user(username="manager", password="s3cret-pw")
    assert user.username == "manager"
    assert user.check_password("s3cret-pw")
    assert user.is_staff is False
    assert user.is_superuser is False


def test_create_superuser():
    admin = User.objects.create_superuser(username="owner", password="s3cret-pw")
    assert admin.is_staff is True
    assert admin.is_superuser is True


def test_user_str_returns_username():
    user = User.objects.create_user(username="manager", password="s3cret-pw")
    assert str(user) == "manager"
