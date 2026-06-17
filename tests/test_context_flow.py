import json
from pathlib import Path

import pytest

from app.audit import AuditStore
from app.handler import PriceHandler
from app.logger import CapturingLogger
from app.service import PriceService

FIXTURES = json.loads(
    (Path(__file__).resolve().parents[1] / "fixtures" / "requests.json").read_text()
)


def build_handler():
    logger = CapturingLogger()
    audit = AuditStore()
    service = PriceService(audit, logger)
    handler = PriceHandler(service)
    return handler, audit, logger


def test_audit_uses_trusted_context_not_body():
    handler, audit, _ = build_handler()
    headers = FIXTURES["trusted_headers"]
    body = FIXTURES["spoofed_body"]
    property_id = FIXTURES["property_id"]

    handler.handle(headers, property_id, body)

    assert len(audit.rows) == 1
    row = audit.rows[0]
    assert row["request_id"] == headers["X-Request-ID"]
    assert row["user_id"] == headers["X-User-ID"]
    assert row["property_id"] == property_id


def test_audit_ignores_client_supplied_correlation_fields():
    handler, audit, _ = build_handler()
    headers = FIXTURES["trusted_headers"]
    body = FIXTURES["spoofed_body"]
    property_id = FIXTURES["property_id"]

    handler.handle(headers, property_id, body)

    row = audit.rows[0]
    assert row["request_id"] != body["request_id"]
    assert row["user_id"] != body["updated_by"]


def test_failure_log_contains_request_id():
    handler, _, logger = build_handler()
    headers = FIXTURES["trusted_headers"]
    body = FIXTURES["invalid_body"]
    property_id = FIXTURES["property_id"]

    with pytest.raises(ValueError):
        handler.handle(headers, property_id, body)

    error_records = [r for r in logger.records if r["level"] == "error"]
    assert error_records, "expected an error log for the failed update"
    assert any(
        r.get("request_id") == headers["X-Request-ID"] for r in error_records
    ), "failure log should carry the trusted request id for correlation"


def test_valid_update_succeeds():
    handler, audit, logger = build_handler()
    headers = FIXTURES["trusted_headers"]
    body = FIXTURES["valid_body"]
    property_id = FIXTURES["property_id"]

    row = handler.handle(headers, property_id, body)

    assert row["price"] == body["price"]
    assert row["property_id"] == property_id
    assert any(r["level"] == "info" for r in logger.records)


def test_invalid_price_is_rejected():
    handler, audit, _ = build_handler()
    headers = FIXTURES["trusted_headers"]
    body = FIXTURES["invalid_body"]
    property_id = FIXTURES["property_id"]

    with pytest.raises(ValueError):
        handler.handle(headers, property_id, body)

    assert audit.rows == []


def test_audit_row_has_no_raw_body_fields():
    handler, audit, _ = build_handler()
    headers = FIXTURES["trusted_headers"]
    body = FIXTURES["spoofed_body"]
    property_id = FIXTURES["property_id"]

    handler.handle(headers, property_id, body)

    row = audit.rows[0]
    assert "updated_by" not in row
    assert set(row.keys()) == {"property_id", "price", "request_id", "user_id"}
