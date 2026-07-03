"""
Tests for narou_json2db module
"""

import os
import sys
from unittest.mock import ANY, MagicMock, patch, mock_open

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import narou_json2db


class TestCheckCount:
    """Tests for check_count function"""

    def test_check_count_success(self, mock_db_connection):
        """Test successful retrieval of counter value"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"parameter_value": 5}
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        with patch("narou_json2db.db_func.db_connect") as mock_connect:
            mock_connect.return_value = mock_db_connection

            result = narou_json2db.check_count()

            assert result == 5
            mock_db_connection.close.assert_called_once()

    def test_check_count_not_found(self, mock_db_connection):
        """Test when counter is not found"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        with patch("narou_json2db.db_func.db_connect") as mock_connect:
            mock_connect.return_value = mock_db_connection

            result = narou_json2db.check_count()

            assert result == -1
            mock_db_connection.close.assert_called_once()


class TestArgumentParser:
    """Tests for command-line argument parsing"""

    def test_build_parser_default_input_file(self):
        parser = narou_json2db.build_parser()

        args = parser.parse_args([])

        assert args.infile == "temp.json"

    def test_build_parser_custom_input_file(self):
        parser = narou_json2db.build_parser()

        args = parser.parse_args(["-i", "custom.json"])

        assert args.infile == "custom.json"


class TestContentRow:
    """Tests for contents_tbl row building"""

    def test_build_content_row_success(self, sample_novel_data):
        novel = sample_novel_data["0"]

        row = narou_json2db.build_content_row(6, novel)

        assert len(row) == len(narou_json2db.CONTENTS_COLUMNS)
        assert row[0] == 6
        assert row[1] == "N0001"
        assert row[2] == "Test Novel 1"
        assert row[-1] == "2024-01-01 12:00:00"

    def test_build_content_row_requires_ncode(self):
        novel_without_ncode = {"title": "Test", "userid": 1}

        with pytest.raises(Exception, match="ncode not found"):
            narou_json2db.build_content_row(1, novel_without_ncode)


class TestInsertContents:
    """Tests for batch insert behavior"""

    def test_insert_contents_empty_iterator(self):
        mock_cursor = MagicMock()

        narou_json2db.insert_contents(mock_cursor, [], 1)

        mock_cursor.executemany.assert_not_called()

    def test_insert_contents_batches_1000_records(self, sample_novel_data):
        mock_cursor = MagicMock()
        base_novel = sample_novel_data["0"]
        data_iterator = [
            (str(i), {**base_novel, "ncode": f"N{i:04d}"})
            for i in range(1500)
        ]

        narou_json2db.insert_contents(mock_cursor, data_iterator, 6)

        assert mock_cursor.executemany.call_count == 2
        first_batch = mock_cursor.executemany.call_args_list[0].args[1]
        second_batch = mock_cursor.executemany.call_args_list[1].args[1]
        assert len(first_batch) == 1000
        assert len(second_batch) == 500
        assert first_batch[0][0] == 6
        assert first_batch[0][1] == "N0000"


class TestMainScript:
    """Tests for main script execution"""

    def test_main_default_input_file(self, mock_db_connection):
        """Test that default input file is temp.json"""
        mock_cursor = MagicMock()
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        with patch("narou_json2db.check_count") as mock_check_count, patch(
            "builtins.open", mock_open(read_data=b"{}")
        ) as mock_file, patch("narou_json2db.db_func.db_connect") as mock_connect, patch(
            "narou_json2db.ijson.kvitems"
        ) as mock_kvitems:
            mock_check_count.return_value = 0
            mock_connect.return_value = mock_db_connection
            mock_kvitems.return_value = []

            result = narou_json2db.main([])

            assert result == 0
            mock_file.assert_called_once_with("temp.json", "rb")
            mock_cursor.execute.assert_any_call(
                "UPDATE parameter_tbl SET parameter_value = %s WHERE parameter_name = 'counter'",
                (1,),
            )
            mock_cursor.execute.assert_any_call(
                "INSERT INTO count_timestamp_tbl SET count = %s, timestamp = %s",
                (1, ANY),
            )
            mock_db_connection.commit.assert_called_once()
            mock_db_connection.close.assert_called_once()

    def test_main_custom_input_file(self, mock_db_connection):
        """Test that custom input file is used with -i option"""
        mock_cursor = MagicMock()
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        with patch("narou_json2db.check_count") as mock_check_count, patch(
            "builtins.open", mock_open(read_data=b"{}")
        ) as mock_file, patch("narou_json2db.db_func.db_connect") as mock_connect, patch(
            "narou_json2db.ijson.kvitems"
        ) as mock_kvitems:
            mock_check_count.return_value = 0
            mock_connect.return_value = mock_db_connection
            mock_kvitems.return_value = []

            result = narou_json2db.main(["-i", "custom.json"])

            assert result == 0
            mock_file.assert_called_once_with("custom.json", "rb")
            mock_db_connection.commit.assert_called_once()
            mock_db_connection.close.assert_called_once()

    def test_main_file_not_found_exits(self):
        """Test handling of missing file"""
        with patch("narou_json2db.check_count") as mock_check_count, patch(
            "narou_json2db.sys.exit", side_effect=SystemExit
        ) as mock_exit:
            mock_check_count.return_value = 0

            with patch("builtins.open") as mock_file:
                mock_file.side_effect = FileNotFoundError("File not found")

                with pytest.raises(SystemExit):
                    narou_json2db.main(["-i", "nonexistent.json"])

                mock_exit.assert_called_once()

    def test_main_invalid_counter_exits(self):
        """Test that script exits when counter is invalid"""
        with patch("narou_json2db.check_count") as mock_check_count, patch(
            "narou_json2db.sys.exit", side_effect=SystemExit
        ) as mock_exit:
            mock_check_count.return_value = -1

            with pytest.raises(SystemExit):
                narou_json2db.main([])

            mock_exit.assert_called_once()

    def test_main_rollback_on_invalid_record(self, mock_db_connection):
        """Test transaction rollback on insert error"""
        mock_cursor = MagicMock()
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        with patch("narou_json2db.check_count") as mock_check_count, patch(
            "builtins.open", mock_open(read_data=b"{}")
        ), patch("narou_json2db.db_func.db_connect") as mock_connect, patch(
            "narou_json2db.ijson.kvitems"
        ) as mock_kvitems:
            mock_check_count.return_value = 0
            mock_connect.return_value = mock_db_connection
            mock_kvitems.return_value = [("0", {"title": "Missing ncode"})]

            result = narou_json2db.main([])

            assert result == 0
            mock_db_connection.rollback.assert_called_once()
            mock_db_connection.commit.assert_not_called()
            mock_db_connection.close.assert_called_once()
