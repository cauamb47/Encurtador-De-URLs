import pytest
from rest_framework.test import APIClient

from .models import Link
from .utils import generate_code


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(username="ana", password="SenhaForte123!")


@pytest.fixture
def other_user(django_user_model):
    return django_user_model.objects.create_user(username="bia", password="SenhaForte123!")


@pytest.fixture # Cliente de API já "logado" como o usuário, sem precisar gerar token
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_generate_code_length_and_charset():
    code = generate_code(8)
    assert len(code) == 8
    assert code.isalnum()


@pytest.mark.django_db
def test_create_link_requires_authentication():
    response = APIClient().post("/api/links/", {"original_url": "https://example.com"}, format="json")
    assert response.status_code == 401


@pytest.mark.django_db # Ao criar, o servidor gera o código e define o dono automaticamente
def test_create_link_sets_owner_and_code(auth_client, user):
    response = auth_client.post("/api/links/", {"original_url": "https://example.com"}, format="json")
    assert response.status_code == 201
    assert len(response.data["code"]) == 6
    assert Link.objects.get(code=response.data["code"]).owner == user


@pytest.mark.django_db # Garante o isolamento: um usuário não enxerga os links de outro
def test_user_only_sees_own_links(auth_client, user, other_user):
    Link.objects.create(owner=user, original_url="https://meu.com")
    Link.objects.create(owner=other_user, original_url="https://alheio.com")
    response = auth_client.get("/api/links/")
    assert response.status_code == 200
    urls = [item["original_url"] for item in response.data]
    assert urls == ["https://meu.com"]


@pytest.mark.django_db
def test_redirect_is_public(user):
    link = Link.objects.create(owner=user, original_url="https://example.com")
    response = APIClient().get(f"/{link.code}/")
    assert response.status_code == 302
    assert response["Location"] == "https://example.com"


@pytest.mark.django_db
def test_inactive_link_returns_404(user):
    link = Link.objects.create(owner=user, original_url="https://example.com", is_active=False)
    response = APIClient().get(f"/{link.code}/")
    assert response.status_code == 404