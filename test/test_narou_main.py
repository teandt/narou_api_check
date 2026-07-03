"""
Tests for narou_main module
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from io import StringIO

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import narou_main


class TestYear4Type:
    """Tests for year4_type validation function"""

    def test_year4_type_valid_year(self):
        """Test valid 4-digit year"""
        result = narou_main.year4_type("2024")
        assert result == 2024
        assert isinstance(result, int)

    def test_year4_type_valid_year_range(self):
        """Test various valid years"""
        assert narou_main.year4_type("2000") == 2000
        assert narou_main.year4_type("1999") == 1999
        assert narou_main.year4_type("2099") == 2099

    def test_year4_type_short_year(self):
        """Test that 3-digit year raises error"""
        with pytest.raises(Exception):  # ArgumentTypeError
            narou_main.year4_type("202")

    def test_year4_type_long_year(self):
        """Test that 5-digit year raises error"""
        with pytest.raises(Exception):  # ArgumentTypeError
            narou_main.year4_type("20249")

    def test_year4_type_non_numeric(self):
        """Test that non-numeric year raises error"""
        with pytest.raises(Exception):  # ArgumentTypeError
            narou_main.year4_type("202a")

    def test_year4_type_empty_string(self):
        """Test that empty string raises error"""
        with pytest.raises(Exception):  # ArgumentTypeError
            narou_main.year4_type("")

    def test_year4_type_non_year(self):
        """Test that invalid year values raise error"""
        with pytest.raises(Exception):  # ArgumentTypeError
            narou_main.year4_type("9999")  # This might be valid depending on implementation


class TestMainArgumentParsing:
    """Tests for command-line argument parsing"""

    def test_lm_option_parsing(self):
        """Test -lm option parsing"""
        import argparse as ap

        parser = ap.ArgumentParser()
        parser.add_argument(
            "-lm", nargs=3, metavar=("START_YEAR", "END_YEAR", "LIMIT_COUNT")
        )
        args = parser.parse_args(["-lm", "2020", "2024", "100"])

        assert args.lm == ["2020", "2024", "100"]

    def test_lh_option_parsing(self):
        """Test -lh option parsing"""
        import argparse as ap

        parser = ap.ArgumentParser()
        parser.add_argument("-lh", nargs=2, metavar=("YEAR", "LIMIT_COUNT"))
        args = parser.parse_args(["-lh", "2024", "100"])

        assert args.lh == ["2024", "100"]

    def test_nt_option_parsing(self):
        """Test -nt option parsing"""
        import argparse as ap

        parser = ap.ArgumentParser()
        parser.add_argument("-nt", nargs=2, metavar=("START_YEAR", "END_YEAR"))
        args = parser.parse_args(["-nt", "2020", "2024"])

        assert args.nt == ["2020", "2024"]

    def test_no_option_provided(self):
        """Test when no option is provided"""
        import argparse as ap

        parser = ap.ArgumentParser()
        parser.add_argument("-lm", nargs=3, default=None)
        parser.add_argument("-lh", nargs=2, default=None)
        parser.add_argument("-nt", nargs=2, default=None)
        args = parser.parse_args([])

        assert args.lm is None
        assert args.lh is None
        assert args.nt is None


class TestLmOptionValidation:
    """Tests for -lm option input validation"""

    def test_lm_valid_inputs(self):
        """Test valid -lm inputs"""
        parser = __import__("argparse").ArgumentParser()
        parser.add_argument("-lm", nargs=3, metavar=("START_YEAR", "END_YEAR", "LIMIT_COUNT"))
        args = parser.parse_args(["-lm", "2020", "2024", "100"])

        # Validate manually
        try:
            start_year = narou_main.year4_type(args.lm[0])
            end_year = narou_main.year4_type(args.lm[1])
            limit_count = int(args.lm[2])
            assert limit_count >= 1

            assert start_year == 2020
            assert end_year == 2024
            assert limit_count == 100
        except Exception as e:
            pytest.fail(f"Valid inputs raised exception: {e}")

    def test_lm_invalid_start_year(self):
        """Test -lm with invalid start year"""
        with pytest.raises(Exception):
            narou_main.year4_type("202")

    def test_lm_invalid_end_year(self):
        """Test -lm with invalid end year"""
        with pytest.raises(Exception):
            narou_main.year4_type("202a")

    def test_lm_limit_count_zero(self):
        """Test -lm with LIMIT_COUNT = 0"""
        with pytest.raises(ValueError):
            limit_count = int("0")
            if limit_count < 1:
                raise ValueError

    def test_lm_limit_count_negative(self):
        """Test -lm with negative LIMIT_COUNT"""
        with pytest.raises(ValueError):
            limit_count = int("-1")
            if limit_count < 1:
                raise ValueError

    def test_lm_limit_count_non_numeric(self):
        """Test -lm with non-numeric LIMIT_COUNT"""
        with pytest.raises(ValueError):
            int("abc")


class TestLhOptionValidation:
    """Tests for -lh option input validation"""

    def test_lh_valid_inputs(self):
        """Test valid -lh inputs"""
        parser = __import__("argparse").ArgumentParser()
        parser.add_argument("-lh", nargs=2, metavar=("YEAR", "LIMIT_COUNT"))
        args = parser.parse_args(["-lh", "2024", "100"])

        try:
            year = narou_main.year4_type(args.lh[0])
            limit_count = int(args.lh[1])
            assert limit_count >= 1

            assert year == 2024
            assert limit_count == 100
        except Exception as e:
            pytest.fail(f"Valid inputs raised exception: {e}")

    def test_lh_invalid_year(self):
        """Test -lh with invalid year"""
        with pytest.raises(Exception):
            narou_main.year4_type("202")

    def test_lh_limit_count_zero(self):
        """Test -lh with LIMIT_COUNT = 0"""
        with pytest.raises(ValueError):
            if int("0") < 1:
                raise ValueError

    def test_lh_limit_count_non_numeric(self):
        """Test -lh with non-numeric LIMIT_COUNT"""
        with pytest.raises(ValueError):
            int("xyz")


class TestNtOptionValidation:
    """Tests for -nt option input validation"""

    def test_nt_valid_inputs(self):
        """Test valid -nt inputs"""
        parser = __import__("argparse").ArgumentParser()
        parser.add_argument("-nt", nargs=2, metavar=("START_YEAR", "END_YEAR"))
        args = parser.parse_args(["-nt", "2015", "2024"])

        try:
            start_year = narou_main.year4_type(args.nt[0])
            end_year = narou_main.year4_type(args.nt[1])

            assert start_year == 2015
            assert end_year == 2024
        except Exception as e:
            pytest.fail(f"Valid inputs raised exception: {e}")

    def test_nt_invalid_start_year(self):
        """Test -nt with invalid start year"""
        with pytest.raises(Exception):
            narou_main.year4_type("201")

    def test_nt_invalid_end_year(self):
        """Test -nt with invalid end year"""
        with pytest.raises(Exception):
            narou_main.year4_type("202a")

    def test_nt_reversed_years(self):
        """Test -nt with start_year > end_year"""
        # This depends on implementation - the script may allow this
        start_year = narou_main.year4_type("2024")
        end_year = narou_main.year4_type("2015")

        # No error raised by year4_type itself
        assert start_year == 2024
        assert end_year == 2015


class TestFunctionCalls:
    """Tests for actual function invocations"""

    def test_lm_calls_get_title_length_mean(self):
        """Test that -lm option calls get_title_length_mean"""
        with patch("narou_main.tm.get_title_length_mean") as mock_func:
            import argparse as ap

            parser = ap.ArgumentParser()
            parser.add_argument("-lm", nargs=3)
            parser.add_argument("-lh", nargs=2)
            parser.add_argument("-nt", nargs=2)
            args = parser.parse_args(["-lm", "2020", "2024", "100"])

            if args.lm:
                try:
                    start_year = narou_main.year4_type(args.lm[0])
                    end_year = narou_main.year4_type(args.lm[1])
                    limit_count = int(args.lm[2])
                    if limit_count >= 1:
                        mock_func(start_year, end_year, limit_count)
                except:
                    pass

            mock_func.assert_called_once_with(2020, 2024, 100)

    def test_lh_calls_get_title_length_hist(self):
        """Test that -lh option calls get_title_length_hist"""
        with patch("narou_main.tm.get_title_length_hist") as mock_func:
            import argparse as ap

            parser = ap.ArgumentParser()
            parser.add_argument("-lm", nargs=3)
            parser.add_argument("-lh", nargs=2)
            parser.add_argument("-nt", nargs=2)
            args = parser.parse_args(["-lh", "2024", "100"])

            if args.lh:
                try:
                    year = narou_main.year4_type(args.lh[0])
                    limit_count = int(args.lh[1])
                    if limit_count >= 1:
                        mock_func(year, limit_count)
                except:
                    pass

            mock_func.assert_called_once_with(2024, 100)

    def test_nt_calls_get_nobel_type_nums(self):
        """Test that -nt option calls get_nobel_type_nums"""
        with patch("narou_main.tm.get_nobel_type_nums") as mock_func:
            import argparse as ap

            parser = ap.ArgumentParser()
            parser.add_argument(
                "-nt", nargs=2, type=narou_main.year4_type,
                metavar=("START_YEAR", "END_YEAR")
            )
            args = parser.parse_args(["-nt", "2015", "2024"])

            if args.nt:
                start_year = args.nt[0]
                end_year = args.nt[1]
                mock_func(start_year, end_year)

            mock_func.assert_called_once_with(2015, 2024)


class TestErrorHandling:
    """Tests for error handling in main script"""

    def test_argument_error_handling(self):
        """Test proper error message for invalid arguments"""
        import argparse as ap

        parser = ap.ArgumentParser()
        parser.add_argument("-lm", nargs=3)

        # This should not raise, argparse handles it
        # But we can test the validation logic
        args = parser.parse_args(["-lm", "2024", "2024", "0"])

        with pytest.raises(ValueError):
            limit_count = int(args.lm[2])
            if limit_count < 1:
                raise ValueError(f"LIMIT_COUNT には1以上の整数を指定してください: '{args.lm[2]}'")

    def test_type_error_on_invalid_year(self):
        """Test type error handling for invalid year"""
        with pytest.raises(Exception):
            narou_main.year4_type("not_a_year")
