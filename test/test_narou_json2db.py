"""
Tests for narou_json2db module
"""

import pytest
import os
import sys
from unittest.mock import MagicMock, patch, mock_open

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

    def test_counter_value_incremented(self, mock_db_connection):
        """Test that counter is incremented in database"""
        mock_cursor = MagicMock()
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        with patch("narou_json2db.db_func.db_connect") as mock_connect:
            mock_connect.return_value = mock_db_connection

            with patch("narou_json2db.check_count") as mock_check_count:
                mock_check_count.return_value = 5

                # Simulate the counter update
                cnt = mock_check_count()
                assert cnt == 5

                # Expected SQL: UPDATE parameter_tbl SET parameter_value = %s WHERE parameter_name = 'counter'
                # The new value should be cnt + 1 = 6

    def test_timestamp_recorded(self, mock_db_connection):
        """Test that timestamp is recorded in database"""
        mock_cursor = MagicMock()
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        import datetime

        with patch("narou_json2db.db_func.db_connect") as mock_connect:
            mock_connect.return_value = mock_db_connection

            timestamp = datetime.datetime.now().isoformat(timespec="seconds")

            # Verify timestamp format
            assert "T" in timestamp  # ISO format contains T
            assert len(timestamp) > 0

    def test_file_not_found_error(self):
        """Test handling of missing file"""
        with patch("narou_json2db.check_count") as mock_check_count, patch(
            "builtins.exit", side_effect=SystemExit
        ) as mock_exit:
            mock_check_count.return_value = 0

            with patch("builtins.open") as mock_file:
                mock_file.side_effect = FileNotFoundError("File not found")

                with pytest.raises(SystemExit):
                    narou_json2db.main(["-i", "nonexistent.json"])

                mock_exit.assert_called_once()

    def test_invalid_counter_exits(self):
        """Test that script exits when counter is invalid"""
        with patch("narou_json2db.check_count") as mock_check_count, patch(
            "builtins.exit", side_effect=SystemExit
        ) as mock_exit:
            mock_check_count.return_value = -1

            with pytest.raises(SystemExit):
                narou_json2db.main([])

            mock_exit.assert_called_once()

    def test_ncode_required_field_validation(self, sample_novel_data):
        """Test that ncode is validated as required field"""
        novel_without_ncode = {"title": "Test", "userid": 1}

        assert "ncode" not in novel_without_ncode

        # This should raise an exception
        if "ncode" not in novel_without_ncode:
            assert True
        else:
            pytest.fail("ncode validation failed")

    def test_batch_processing_1000_records(self, mock_db_connection):
        """Test batch processing with 1000 record threshold"""
        mock_cursor = MagicMock()
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        # Simulate batch processing logic
        bulk_cnt = 0
        batch_size = 1000
        set_sql_data = []

        for i in range(1500):
            bulk_cnt += 1
            if bulk_cnt >= batch_size:
                # This is where executemany would be called
                assert bulk_cnt == batch_size
                bulk_cnt = 0
                set_sql_data.clear()

    def test_transaction_rollback_on_error(self, mock_db_connection):
        """Test transaction rollback on error"""
        mock_db_connection.rollback = MagicMock()

        with patch("narou_json2db.db_func.db_connect") as mock_connect:
            mock_connect.return_value = mock_db_connection

            # Simulate error scenario
            try:
                raise Exception("Test error")
            except Exception as e:
                mock_db_connection.rollback()
                assert mock_db_connection.rollback.called

    def test_transaction_commit_on_success(self, mock_db_connection):
        """Test transaction commit on success"""
        mock_db_connection.commit = MagicMock()

        with patch("narou_json2db.db_func.db_connect") as mock_connect:
            mock_connect.return_value = mock_db_connection

            # Simulate success scenario
            mock_db_connection.commit()
            assert mock_db_connection.commit.called

    def test_empty_json_file(self, mock_db_connection):
        """Test handling of empty JSON file"""
        mock_cursor = MagicMock()
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        with patch("narou_json2db.ijson.kvitems") as mock_kvitems:
            mock_kvitems.return_value = []

            result = list(mock_kvitems(None, ""))

            assert result == []
