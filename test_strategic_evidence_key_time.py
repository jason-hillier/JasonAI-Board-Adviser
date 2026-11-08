"""Tests for Macian signing-key timestamp validation."""

from datetime import datetime, timezone

import pytest

from strategic_evidence_key_time import parse_key_timestamp


def test_utc_timestamp():
    result = parse_key_timestamp("2026-11-08T12:00:00+00:00")
    assert result == datetime(2026, 11, 8, 12, 0, tzinfo=timezone.utc)


def test_timezone_offset_normalised_to_utc():
    result = parse_key_timestamp("2026-11-08T14:00:00+02:00")
    assert result == datetime(2026, 11, 8, 12, 0, tzinfo=timezone.utc)


def test_negative_timezone_offset():
    result = parse_key_timestamp("2026-11-08T07:00:00-05:00")
    assert result == datetime(2026, 11, 8, 12, 0, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    "value",
    [
        "",
        "not-a-date",
        "2026-11-08T12:00:00",
        "2026-13-08T12:00:00+00:00",
        None,
        12345,
    ],
)
def test_invalid_timestamps_rejected(value):
    with pytest.raises(ValueError):
        parse_key_timestamp(value)
