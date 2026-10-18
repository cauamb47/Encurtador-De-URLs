import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_register_creates_user_without_exposing_password():
    # O cadastro funciona e a senha nunca volta na resposta
    response = APIClient().post(
        "/api/auth/register/",
        {"username": "caua", "email": "c@example.com", "password": "SenhaForte123!"},
        format="json",
    )
    assert response.status_code == 201
    assert "password" not in response.data


@pytest.mark.django_db # Senha fraca é recusada (400) pelas regras de validação do Django
def test_register_rejects_weak_password():
    # Senha fraca é recusada (400) pelas regras de validação do Django
    response = APIClient().post(
        "/api/auth/register/",
        {"username": "caua", "password": "123"},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_login_returns_tokens(django_user_model):
    # Login com credenciais corretas devolve os tokens access e refresh
    django_user_model.objects.create_user(username="caua", password="SenhaForte123!")
    response = APIClient().post(
        "/api/auth/token/",
        {"username": "caua", "password": "SenhaForte123!"},
        format="json",
    )
    assert response.status_code == 200
    assert "access" in response.data and "refresh" in response.data