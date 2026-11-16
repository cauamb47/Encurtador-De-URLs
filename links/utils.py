import secrets
import string

ALPHABET = string.ascii_letters + string.digits  # 62 caracteres (base62)

# Sorteia 'length' caracteres do alfabeto e junta numa string (ex: "rUgEtH").
def generate_code(length: int = 6) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))

def parse_browser(user_agent: str) -> str:
    # Classifica o navegador pelo texto do user agent.
    ua = user_agent.lower()
    if "edg/" in ua or "edge/" in ua:
        return "Edge"
    if "opr/" in ua or "opera" in ua:
        return "Opera"
    if "firefox" in ua or "fxios" in ua:
        return "Firefox"
    if "chrome" in ua or "crios" in ua:
        return "Chrome"
    if "safari" in ua:
        return "Safari"
    return "Outro"