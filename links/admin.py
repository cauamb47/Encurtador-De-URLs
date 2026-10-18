from django.contrib import admin

from .models import Click, Link


@admin.register(Link) # Registra o model no painel /admin/ e define as colunas e a busca
class LinkAdmin(admin.ModelAdmin):
    list_display = ("code", "original_url", "owner", "is_active", "created_at")
    search_fields = ("code", "original_url")


@admin.register(Click)
class ClickAdmin(admin.ModelAdmin):
    list_display = ("link", "clicked_at", "ip_address")