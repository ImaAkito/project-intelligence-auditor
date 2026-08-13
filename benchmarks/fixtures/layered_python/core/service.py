from storage.repository import save


def execute(payload: str) -> str:
    value = payload.strip().upper()
    save(value)
    return value
