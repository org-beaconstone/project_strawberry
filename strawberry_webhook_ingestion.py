"""Billing webhook ingestion for the Strawberry platform.

Receives inbound billing provider webhooks (payment succeeded,
invoice finalized, etc.) and writes the parsed usage event to the
usage ledger, retrying transient failures.
"""

import time

from strawberry_errors import log_retry_log_failure


MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2


def ingest_webhook_event(customer_id: str, webhook_event: dict) -> bool:
    """Parse an inbound webhook event and write it to the usage ledger.

    Retries transient ledger write failures. If retries are
    exhausted, logs error_code=RETRY_LOG_FAILURE via the shared
    error helper.
    """
    attempt = 0
    last_error = None
    while attempt < MAX_RETRIES:
        attempt += 1
        try:
            return _write_event_to_ledger(customer_id, webhook_event)
        except LedgerWriteError as exc:
            last_error = exc
            time.sleep(RETRY_BACKOFF_SECONDS * attempt)

    log_retry_log_failure(
        service="usage-metering-service",
        sink="usage_ledger_write",
        customer_id=customer_id,
        event_id=webhook_event.get("id"),
        retry_attempts=attempt,
        max_retries=MAX_RETRIES,
        last_error=str(last_error),
    )
    return False


def _write_event_to_ledger(customer_id: str, webhook_event: dict) -> bool:
    """Write a parsed webhook event to the usage ledger. Raises LedgerWriteError on failure."""
    raise NotImplementedError


class LedgerWriteError(Exception):
    """Raised when the usage ledger rejects or fails to accept a write."""
