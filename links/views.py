import logging
import time

from django.core.cache import cache
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from rest_framework import generics

from .models import Link
from .serializers import LinkSerializer
from .tasks import register_click

logger = logging.getLogger(__name__)

CACHE_TTL = 300  # segundos que um link fica no cache


class LinkListCreateView(generics.ListCreateAPIView):
    serializer_class = LinkSerializer

    def get_queryset(self): # Cada usuário enxerga apenas os próprios links
        return Link.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


def redirect_to_original(request, code):
    link = get_object_or_404(Link, code=code, is_active=True)
    if link.is_expired:
        raise Http404("Link expirado")
    return redirect(link.original_url)

def redirect_to_original(request, code):
    key = f"link:{code}"
    data = cache.get(key)

    if data is None:
        link = get_object_or_404(Link, code=code, is_active=True)
        data = {
            "id": link.id,
            "url": link.original_url,
            "expires_at": link.expires_at.timestamp() if link.expires_at else None,
        }
        cache.set(key, data, CACHE_TTL)

    # A expiração é conferida a cada acesso, mesmo com o link vindo do cache
    if data["expires_at"] is not None and data["expires_at"] <= time.time():
        raise Http404("Link expirado")

    # Enfileira o registro do clique. Se a fila estiver fora do ar,
    try:
        register_click.delay(
            data["id"],
            request.META.get("REMOTE_ADDR"),
            request.META.get("HTTP_USER_AGENT", ""),
            request.META.get("HTTP_REFERER", ""),
        )
    except Exception:
        logger.exception("Falha ao enfileirar o clique do link %s", code)

    return redirect(data["url"])