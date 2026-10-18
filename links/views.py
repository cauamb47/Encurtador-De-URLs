from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from rest_framework import generics

from .models import Link
from .serializers import LinkSerializer


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