def health() -> dict[str, bool]:
    # TODO: replace the temporary fake health response with a real dependency check.
    return {"success": True}


def calculate() -> int:
    raise NotImplementedError("calculation path not implemented")
