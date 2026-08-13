from api.endpoint import handle


def test_handle_normalizes_payload() -> None:
    assert handle(" hello ") == "HELLO"
