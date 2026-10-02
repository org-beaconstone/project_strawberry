"""Scheduled usage reconciliation for the Strawberry platform.

Periodically compares usage records against the usage ledger and
replays any records missing from the ledger, retrying transient
write failures.
"""

import time

from strawberry_errors import log_retry_log_failure


MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2


def reconcile_usage_record(customer_id: str, usage_record: dict) -> bool:
    """Replay a usage record missing from the usage ledger.

    Retries transient ledger write failures. If retries are
    exhausted, logs error_code=RETRY_LOG_FAILURE via the shared
    error helper.
    """
    attempt = 0
    last_error = None
    while attempt < MAX_RETRIES:
        attempt += 1
        try:
            return _replay_record_to_ledger(customer_id, usage_record)
        except LedgerWriteError as exc:
            last_error = exc
            time.sleep(RETRY_BACKOFF_SECONDS * attempt)

    log_retry_log_failure(
        service="usage-metering-service",
        sink="usage_ledger_write",
        customer_id=customer_id,
        event_id=usage_record.get("id"),
        retry_attempts=attempt,
        max_retries=MAX_RETRIES,
        last_error=str(last_error),
    )
    return False


def _replay_record_to_ledger(customer_id: str, usage_record: dict) -> bool:
    """Replay a usage record to the usage ledger. Raises LedgerWriteError on failure."""
    raise NotImplementedError


class LedgerWriteError(Exception):
    """Raised when the usage ledger rejects or fails to accept a write."""
