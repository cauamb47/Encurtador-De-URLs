from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def use_local_cache(settings):
    # Nos testes, o cache fica na memória do processo, sem tocar no Redis real
    settings.CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
    from django.core.cache import cache

    cache.clear()


@pytest.fixture(autouse=True)
def no_real_queue():
    # Nenhum teste enfileira tarefas de verdade, para não sujar o Redis de desenvolvimento
    with patch("links.views.register_click.delay"):
        yield