from django.conf import settings
from django.db import models
from django.utils import timezone

from .utils import generate_code


class Link(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="links",
        null=True,
        blank=True,
    )
    original_url = models.URLField(max_length=2048)
    code = models.CharField(max_length=10, unique=True, db_index=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.code} -> {self.original_url}"

    def save(self, *args, **kwargs):
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


class Click(models.Model):
    link = models.ForeignKey(Link, on_delete=models.CASCADE, related_name="clicks")
    clicked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)
    referer = models.CharField(max_length=2048, blank=True)

    class Meta:
        ordering = ["-clicked_at"]