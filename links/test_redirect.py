from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from .models import Click, Link
from .tasks import register_click


@pytest.fixture
def link(django_user_model):
    user = django_user_model.objects.create_user(username="ana", password="SenhaForte123!")
    return Link.objects.create(owner=user, original_url="https://example.com")


@pytest.mark.django_db
def test_redirect_enqueues_click(link):
    # O redirecionamento enfileira a tarefa com os dados do visitante
    with patch("links.views.register_click.delay") as mock_delay:
        response = APIClient().get(f"/{link.code}/", HTTP_USER_AGENT="pytest", HTTP_REFERER="https://google.com")
    assert response.status_code == 302
    mock_delay.assert_called_once()
    args = mock_delay.call_args.args
    assert args[0] == link.id
    assert args[2] == "pytest"
    assert args[3] == "https://google.com"


@pytest.mark.django_db
def test_second_redirect_uses_cache(link, django_assert_num_queries):
    # A 1ª visita consulta o banco e grava no cache; a 2ª não faz nenhuma consulta
    client = APIClient()
    client.get(f"/{link.code}/")
    with django_assert_num_queries(0):
        response = client.get(f"/{link.code}/")
    assert response.status_code == 302


@pytest.mark.django_db
def test_deactivating_link_invalidates_cache(link):
    # Desativar o link apaga o cache, então o redirecionamento deixa de funcionar na hora
    client = APIClient()
    client.get(f"/{link.code}/")
    link.is_active = False
    link.save()
    assert client.get(f"/{link.code}/").status_code == 404


@pytest.mark.django_db
def test_register_click_task_saves_click(link):
    # Chamar a tarefa diretamente executa o código na hora, sem precisar do worker
    register_click(link.id, "127.0.0.1", "pytest", "")
    click = Click.objects.get()
    assert click.link == link
    assert click.ip_address == "127.0.0.1"


@pytest.mark.django_db
def test_redirect_works_when_queue_is_down(link):
    # Se a fila falhar, o usuário ainda é redirecionado normalmente
    with patch("links.views.register_click.delay", side_effect=Exception("broker offline")):
        response = APIClient().get(f"/{link.code}/")
    assert response.status_code == 302