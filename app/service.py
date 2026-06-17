"""Business flow for updating a property's price.

Validates the incoming price and, on success, writes an audit row. On failure
it logs the problem so the issue can be investigated.
"""
from app.audit import AuditStore
from app.context import RequestContext
from app.logger import CapturingLogger


class PriceService:
    def __init__(self, audit: AuditStore, logger: CapturingLogger) -> None:
        self._audit = audit
        self._logger = logger

    def update_price(self, ctx: RequestContext, price: int) -> dict:
        if not isinstance(price, int) or isinstance(price, bool) or price <= 0:
            self._logger.error("price update failed: invalid price", **ctx.as_log_fields())
            raise ValueError("invalid price")

        row = self._audit.save_price_audit(ctx, price)
        self._logger.info("price updated", **ctx.as_log_fields())
        return row
