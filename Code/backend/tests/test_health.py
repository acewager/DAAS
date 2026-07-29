"""Smoke test for the platform health endpoint."""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_health_endpoint_returns_200():
    client = APIClient()
    response = client.get(reverse("health-check"))

    assert response.status_code == 200
    assert response.data["success"] is True
    assert "status" in response.data["data"]
