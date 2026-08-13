from __future__ import annotations


def load_service_health() -> dict[str, object]:
    return {
        "status": "success",
        "source": "demo",
        "services": [
            {"name": "api", "status": "healthy", "latency_ms": 42},
            {"name": "worker", "status": "healthy", "latency_ms": 51},
        ],
        "open_incidents": 0,
    }


def render_dashboard() -> str:
    payload = load_service_health()
    cards = "".join(
        f"<article><h2>{item['name']}</h2><p>{item['status']}</p></article>"
        for item in payload["services"]
    )
    return (
        "<html><head><title>Atlas</title></head><body>"
        "<header><h1>Operations Command Center</h1></header>"
        f"<main>{cards}</main>"
        "</body></html>"
    )


if __name__ == "__main__":
    print(render_dashboard())
