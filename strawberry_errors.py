"""Shared error reporting for Strawberry billing/usage services.

Wraps the structured logging API (v2). Unlike Nova's legacy v1 API
(see nova_errors.py), v2 accepts structured fields directly, so every
RETRY_LOG_FAILURE log line carries full context (customer_id,
event_id, retry_attempts, last_error, and trace context) and is
searchable and correlatable after the fact.
"""

from strawberry.logging.v2 import log_event  # logging API v2, structured fields


RETRY_LOG_FAILURE = "RETRY_LOG_FAILURE"


def log_retry_log_failure(
    service: str,
    sink: str,
    customer_id: str,
    event_id: str,
    retry_attempts: int,
    max_retries: int,
    last_error: str,
) -> None:
    """Log that retries were exhausted writing/logging a usage event.

    error_code: RETRY_LOG_FAILURE. Every field is passed through as a
    structured kwarg, so nothing is dropped and the log line
    correlates back to the originating event.
    """
    log_event(
        level="ERROR",
        message="Failed to log usage event after max retry attempts",
        error_code=RETRY_LOG_FAILURE,
        service=service,
        sink=sink,
        customer_id=customer_id,
        event_id=event_id,
        retry_attempts=retry_attempts,
        max_retries=max_retries,
        last_error=last_error,
    )
