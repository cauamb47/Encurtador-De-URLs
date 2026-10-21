from celery import shared_task

from .models import Click


@shared_task
def register_click(link_id, ip_address, user_agent, referer):
    # Roda no worker, fora da requisição: grava o clique sem atrasar o redirecionamento.
    # Corta os textos no tamanho máximo das colunas para evitar erro no banco.
    Click.objects.create(
        link_id=link_id,
        ip_address=ip_address,
        user_agent=user_agent[:512],
        referer=referer[:2048],
    )