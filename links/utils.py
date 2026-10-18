import secrets
import string

ALPHABET = string.ascii_letters + string.digits  # 62 caracteres (base62)

# Sorteia 'length' caracteres do alfabeto e junta numa string (ex: "rUgEtH").
def generate_code(length: int = 6) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))