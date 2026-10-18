from rest_framework import serializers

from .models import Link


class LinkSerializer(serializers.ModelSerializer):
    short_url = serializers.SerializerMethodField()

    class Meta:
        model = Link
        fields = ["id", "original_url", "code", "short_url", "is_active", "created_at", "expires_at"]
        read_only_fields = ["id", "code", "short_url", "created_at", "is_active"]

    def get_short_url(self, obj): # Monta a URL completa (ex: http://localhost:8000/rGgEtH/) usando o domínio da requisição
        request = self.context.get("request")
        path = f"/{obj.code}/"
        return request.build_absolute_uri(path) if request else path