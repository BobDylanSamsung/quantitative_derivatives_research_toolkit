from datetime import UTC, datetime

from derivative_pricing.calibration.option_chain import select_target_expirations


def test_select_target_expirations() -> None:
    expirations = [
        "2026-07-20",
        "2026-07-31",
        "2026-08-21",
        "2026-10-16",
        "2027-01-15",
    ]

    result = select_target_expirations(
        expirations=expirations,
        as_of=datetime(
            2026,
            7,
            18,
            tzinfo=UTC,
        ),
        target_days=(30, 90, 180),
    )

    assert result == [
        "2026-08-21",
        "2026-10-16",
        "2027-01-15",
    ]
