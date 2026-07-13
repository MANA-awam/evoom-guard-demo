"""Negative control used to verify the started_incomplete lifecycle state."""

import time


def test_exceeds_judge_deadline() -> None:
    time.sleep(30)
