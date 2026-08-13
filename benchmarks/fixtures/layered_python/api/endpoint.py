from core.service import execute


def handle(payload: str) -> str:
    return execute(payload)
