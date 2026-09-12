"""
Tests for the PROCESS layer of expense_tracker.py.

These functions were deliberately written with no print()/input() calls
inside them, which is exactly what makes them testable in isolation here -
no mocking of stdin/stdout required.
"""

import pytest

from expense_tracker import accumulate, is_sentinel, parse_amount


class TestParseAmount:
    def test_valid_integer_string(self):
        assert parse_amount("50") == 50.0

    def test_valid_decimal_string(self):
        assert parse_amount("62.3") == 62.3

    def test_rounds_to_two_decimal_places(self):
        assert parse_amount("19.999") == 20.0

    def test_non_numeric_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_amount("abc")

    def test_empty_string_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_amount("")

    def test_zero_is_rejected(self):
        with pytest.raises(ValueError):
            parse_amount("0")

    def test_negative_is_rejected(self):
        with pytest.raises(ValueError):
            parse_amount("-10")

    def test_whitespace_padded_number_is_accepted(self):
        # read_raw_input() strips whitespace before this is called, but the
        # function itself should also tolerate it since float() does.
        assert parse_amount("  15.5  ") == 15.5


class TestAccumulate:
    def test_adds_to_zero(self):
        assert accumulate(0.0, 4.5) == 4.5

    def test_adds_to_existing_total(self):
        assert accumulate(66.8, 35.0) == 101.8

    def test_running_total_across_multiple_calls(self):
        total = 0.0
        for amount in (4.5, 62.3, 35.0, 28.0):
            total = accumulate(total, amount)
        assert total == 129.8

    def test_rounds_floating_point_noise(self):
        # Classic float artifact: 0.1 + 0.2 == 0.30000000000000004 in raw Python.
        assert accumulate(0.1, 0.2) == 0.3


class TestIsSentinel:
    @pytest.mark.parametrize("value", ["quit", "exit", "stop", "QUIT", "Exit", "STOP"])
    def test_recognizes_sentinels_case_insensitively(self, value):
        assert is_sentinel(value) is True

    @pytest.mark.parametrize("value", ["Coffee", "50", "", "quitter", " quit"])
    def test_rejects_non_sentinels(self, value):
        assert is_sentinel(value) is False
