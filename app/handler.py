"""Request boundary for PATCH /properties/{property_id}/price.

Builds the request context from the incoming request and delegates to the
service. The gateway in front of this service assigns X-Request-ID and
X-User-ID headers for every request.
"""
from app.context import RequestContext
from app.service import PriceService


class PriceHandler:
    def __init__(self, service: PriceService) -> None:
        self._service = service

    def handle(self, headers: dict, property_id: str, body: dict) -> dict:
        ctx = RequestContext(
            request_id=headers.get("X-Request-ID", ""),
            user_id=headers.get("X-User-ID", ""),
            property_id=property_id,
        )
        price = body.get("price")
        return self._service.update_price(ctx, price)
