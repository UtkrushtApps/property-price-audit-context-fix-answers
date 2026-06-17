# Solution Steps

1. Inspect the request boundary in app/handler.py and identify the trust boundary: X-Request-ID and X-User-ID are assigned by the gateway, while request_id and updated_by in the body are client-controlled and must not be trusted.

2. Change PriceHandler.handle so it constructs RequestContext.request_id from headers['X-Request-ID'] and RequestContext.user_id from headers['X-User-ID']. Keep RequestContext.property_id sourced from the URL path argument, property_id.

3. Continue reading only the price value from the body, because price is the business payload being validated and updated.

4. Leave AuditStore.save_price_audit unchanged so audit rows are written from the trusted RequestContext and contain only property_id, price, request_id, and user_id.

5. Update PriceService.update_price so validation failures log structured correlation metadata from the trusted context before raising ValueError. Passing **ctx.as_log_fields() ensures the error log includes request_id and other safe correlation fields.

6. Do not change the existing price validation rule: the price must be an int, must not be a bool, and must be greater than zero.

7. Run pytest to verify spoofed body correlation fields are ignored, audit rows use gateway/path context, invalid prices are rejected without audit writes, and validation failure logs include the trusted request_id.

