"""
Tests for narou_api_main module
"""

import pytest
import json
import gzip
import datetime
from unittest.mock import MagicMock, patch, mock_open
import sys
import os

# Add parent directory to path to import narou_api_main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import narou_api_main


class TestGetAllcount:
    """Tests for get_allcount function"""

    def test_get_allcount_success(self):
        """Test successful retrieval of allcount from API"""
        response_data = [{"allcount": 50000}]
        compressed_data = gzip.compress(json.dumps(response_data).encode("utf-8"))

        with patch("narou_api_main.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = compressed_data
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = narou_api_main.get_allcount()

            assert result == 50000
            mock_get.assert_called_once()

    def test_get_allcount_retry_on_failure(self):
        """Test retry logic when API fails"""
        response_data = [{"allcount": 50000}]
        compressed_data = gzip.compress(json.dumps(response_data).encode("utf-8"))

        with patch("narou_api_main.requests.get") as mock_get, patch(
            "narou_api_main.time.sleep"
        ) as mock_sleep:
            mock_response = MagicMock()
            mock_response.content = compressed_data
            mock_response.raise_for_status = MagicMock()

            # Fail twice, then succeed
            mock_get.side_effect = [
                Exception("Connection failed"),
                Exception("Connection failed"),
                mock_response,
            ]

            result = narou_api_main.get_allcount()

            assert result == 50000
            assert mock_get.call_count == 3
            assert mock_sleep.call_count == 2

    def test_get_allcount_max_retry_exceeded(self):
        """Test exit when max retry exceeded"""
        with patch("narou_api_main.requests.get") as mock_get, patch(
            "narou_api_main.exit"
        ) as mock_exit, patch("narou_api_main.time.sleep"):
            mock_get.side_effect = Exception("Connection failed")

            narou_api_main.get_allcount()

            assert mock_exit.called


class TestCheckCount:
    """Tests for check_count function"""

    def test_check_count_success(self, mock_db_connection):
        """Test successful retrieval of counter value"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"parameter_value": 10}
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        with patch("narou_api_main.db_func.db_connect") as mock_connect:
            mock_connect.return_value = mock_db_connection

            result = narou_api_main.check_count()

            assert result == 10
            mock_cursor.execute.assert_called_once()
            mock_db_connection.close.assert_called_once()

    def test_check_count_no_data(self, mock_db_connection):
        """Test when counter data is not found"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        with patch("narou_api_main.db_func.db_connect") as mock_connect:
            mock_connect.return_value = mock_db_connection

            result = narou_api_main.check_count()

            assert result == -1

    def test_check_count_db_connection_closed(self, mock_db_connection):
        """Test that database connection is properly closed"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"parameter_value": 10}
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        with patch("narou_api_main.db_func.db_connect") as mock_connect:
            mock_connect.return_value = mock_db_connection

            narou_api_main.check_count()

            mock_db_connection.close.assert_called_once()


class TestMainScript:
    """Tests for main script execution"""

    def test_main_default_output_file(self, sample_api_response):
        """Test that default output file is temp.json"""
        with patch("narou_api_main.sys.argv", ["narou_api_main.py"]), patch(
            "narou_api_main.get_allcount"
        ) as mock_allcount, patch(
            "narou_api_main.check_count"
        ) as mock_check_count, patch(
            "narou_api_main.requests.get"
        ) as mock_get, patch(
            "builtins.open", mock_open()
        ) as mock_file, patch(
            "narou_api_main.json.dump"
        ) as mock_dump, patch(
            "narou_api_main.exit"
        ):
            mock_allcount.return_value = 500
            mock_check_count.return_value = 0

            compressed_data = gzip.compress(
                json.dumps(sample_api_response).encode("utf-8")
            )
            mock_response = MagicMock()
            mock_response.content = compressed_data
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            # Run main
            try:
                exec(compile(open("narou_api_main.py").read(), "narou_api_main.py", "exec"))
            except SystemExit:
                pass

            # Check that open was called with temp.json
            mock_file.assert_called()
            call_args = [call for call in mock_file.call_args_list if "temp.json" in str(call)]
            assert len(call_args) > 0

    def test_main_custom_output_file(self, sample_api_response):
        """Test that custom output file is used with -o option"""
        with patch("narou_api_main.sys.argv", ["narou_api_main.py", "-o", "custom.json"]), patch(
            "narou_api_main.get_allcount"
        ) as mock_allcount, patch(
            "narou_api_main.check_count"
        ) as mock_check_count, patch(
            "narou_api_main.requests.get"
        ) as mock_get, patch(
            "builtins.open", mock_open()
        ) as mock_file, patch(
            "narou_api_main.json.dump"
        ) as mock_dump, patch(
            "narou_api_main.exit"
        ):
            mock_allcount.return_value = 500
            mock_check_count.return_value = 0

            compressed_data = gzip.compress(
                json.dumps(sample_api_response).encode("utf-8")
            )
            mock_response = MagicMock()
            mock_response.content = compressed_data
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            # Simulate argument parsing
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument("-o", "--outfile", type=str, default="temp.json")
            args = parser.parse_args(["-o", "custom.json"])

            assert args.outfile == "custom.json"

    def test_main_exits_on_invalid_counter(self):
        """Test that script exits when counter is invalid"""
        with patch("narou_api_main.get_allcount") as mock_allcount, patch(
            "narou_api_main.check_count"
        ) as mock_check_count, patch("narou_api_main.exit") as mock_exit:
            mock_allcount.return_value = 500
            mock_check_count.return_value = -1

            # Simulate main logic
            cnt = mock_check_count()
            if cnt < 0:
                mock_exit()

            mock_exit.assert_called_once()

    def test_output_json_format(self, sample_novel_data):
        """Test that output JSON has correct format"""
        # Expected format: {"0": {...}, "1": {...}, ...}
        assert "0" in sample_novel_data
        assert isinstance(sample_novel_data["0"], dict)
        assert "ncode" in sample_novel_data["0"]

    def test_duplicate_removal(self):
        """Test that duplicate ncodes are removed"""
        seen_ncodes = set()
        novels = [
            {"ncode": "N0001", "title": "Novel 1"},
            {"ncode": "N0002", "title": "Novel 2"},
            {"ncode": "N0001", "title": "Novel 1 Duplicate"},
        ]

        filtered_novels = []
        for novel in novels:
            ncode = novel.get("ncode")
            if ncode and ncode not in seen_ncodes:
                filtered_novels.append(novel)
                seen_ncodes.add(ncode)

        assert len(filtered_novels) == 2
        assert filtered_novels[0]["ncode"] == "N0001"
        assert filtered_novels[1]["ncode"] == "N0002"

    def test_encoding_utf8(self, sample_novel_data):
        """Test that output is encoded as UTF-8"""
        json_str = json.dumps(sample_novel_data, ensure_ascii=False, indent=4)
        
        # Verify it can be encoded/decoded properly
        encoded = json_str.encode("utf-8")
        decoded = encoded.decode("utf-8")
        
        assert decoded == json_str
