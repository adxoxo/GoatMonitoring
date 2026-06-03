"""Tests for admin JWT auth endpoints (token obtain + refresh)."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

User = get_user_model()
TOKEN_URL = "/api/v1/auth/token/"
REFRESH_URL = "/api/v1/auth/token/refresh/"


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def admin_user():
    return User.objects.create_user(username="owner", password="goat-pw-123")


def test_login_returns_jwt_pair(client, admin_user):
    resp = client.post(
        TOKEN_URL, {"username": "owner", "password": "goat-pw-123"}, format="json"
    )
    assert resp.status_code == 200
    assert "access" in resp.data
    assert "refresh" in resp.data


def test_invalid_credentials_returns_401(client, admin_user):
    resp = client.post(
        TOKEN_URL, {"username": "owner", "password": "wrong"}, format="json"
    )
    assert resp.status_code == 401


def test_refresh_token_returns_new_access_token(client, admin_user):
    login = client.post(
        TOKEN_URL, {"username": "owner", "password": "goat-pw-123"}, format="json"
    )
    resp = client.post(REFRESH_URL, {"refresh": login.data["refresh"]}, format="json")
    assert resp.status_code == 200
    assert "access" in resp.data
