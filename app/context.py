"""Request context model for the price-update flow.

A RequestContext is a small, immutable-ish bag of correlation metadata that
travels alongside a request so that audit writes and logs can be tied back to
the originating request.
"""
from dataclasses import dataclass


@dataclass
class RequestContext:
    request_id: str
    user_id: str
    property_id: str

    def as_log_fields(self) -> dict:
        """Return a small dict of safe correlation fields for structured logs."""
        return {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "property_id": self.property_id,
        }
