from django.conf import settings
from django.db import models
from django.utils import timezone

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .utils import generate_code


class Link(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="links",
    )
        
    original_url = models.URLField(max_length=2048)
    code = models.CharField(max_length=10, unique=True, db_index=True, blank=True)
    is_active = models.BooleanField(default=True) # permite desativar sem apagar
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.code} -> {self.original_url}"

    def save(self, *args, **kwargs): # Antes de salvar, gera o código curto se o link ainda não tiver um
        if not self.code:
            self.code = self._unique_code()
        super().save(*args, **kwargs)

    @staticmethod
    def _unique_code() -> str:
        while True:
            code = generate_code()
            if not Link.objects.filter(code=code).exists():
                return code

    @property
    def is_expired(self) -> bool:
        return self.expires_at is not None and self.expires_at <= timezone.now()

    # Signal: roda automaticamente depois de salvar ou apagar um Link.
    # Remove a entrada do cache para o redirecionamento nunca usar dados desatualizados.
    @receiver([post_save, post_delete], sender=Link)
    def invalidate_link_cache(sender, instance, **kwargs):
        cache.delete(f"link:{instance.code}")


class Click(models.Model): # Registro de cada acesso a um link (usado nas estatísticas)
    link = models.ForeignKey(Link, on_delete=models.CASCADE, related_name="clicks")
    clicked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)
    referer = models.CharField(max_length=2048, blank=True)

    class Meta:
        ordering = ["-clicked_at"]