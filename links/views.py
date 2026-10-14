from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from rest_framework import generics

from .models import Link
from .serializers import LinkSerializer


class LinkListCreateView(generics.ListCreateAPIView):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer


def redirect_to_original(request, code):
    link = get_object_or_404(Link, code=code, is_active=True)
    if link.is_expired:
        raise Http404("Link expirado")
    return redirect(link.original_url)