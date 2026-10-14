import pytest
from rest_framework.test import APIClient

from .models import Link
from .utils import generate_code


def test_generate_code_length_and_charset():
    code = generate_code(8)
    assert len(code) == 8
    assert code.isalnum()


@pytest.mark.django_db
def test_create_link_returns_code():
    client = APIClient()
    response = client.post("/api/links/", {"original_url": "https://example.com"}, format="json")
    assert response.status_code == 201
    assert len(response.data["code"]) == 6


@pytest.mark.django_db
def test_redirect_to_original_url():
    link = Link.objects.create(original_url="https://example.com")
    response = APIClient().get(f"/{link.code}/")
    assert response.status_code == 302
    assert response["Location"] == "https://example.com"


@pytest.mark.django_db
def test_inactive_link_returns_404():
    link = Link.objects.create(original_url="https://example.com", is_active=False)
    response = APIClient().get(f"/{link.code}/")
    assert response.status_code == 404