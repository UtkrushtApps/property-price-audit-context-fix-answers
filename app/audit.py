"""Audit store for property price changes.

save_price_audit records one row per successful price change. The recorded
correlation metadata is meant to be trustworthy for support and compliance.
"""
from app.context import RequestContext


class AuditStore:
    def __init__(self) -> None:
        self.rows: list[dict] = []

    def save_price_audit(self, ctx: RequestContext, price: int) -> dict:
        row = {
            "property_id": ctx.property_id,
            "price": price,
            "request_id": ctx.request_id,
            "user_id": ctx.user_id,
        }
        self.rows.append(row)
        return row
