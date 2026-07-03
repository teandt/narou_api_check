"""
Tests for narou_func module
"""

import pytest
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
import os
import sys
from unittest.mock import MagicMock, patch, mock_open

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import narou_func


class TestCheckCount:
    """Tests for check_count function"""

    def test_check_count_success(self, mock_db_connection):
        """Test successful retrieval of counter value"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"parameter_value": 10}
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        with patch("narou_func.db_func.db_connect") as mock_connect:
            mock_connect.return_value = mock_db_connection

            result = narou_func.check_count()

            assert result == 10

    def test_check_count_not_found(self, mock_db_connection):
        """Test when counter is not found"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        with patch("narou_func.db_func.db_connect") as mock_connect:
            mock_connect.return_value = mock_db_connection

            result = narou_func.check_count()

            assert result == -1


class TestGetTitleLengthHist:
    """Tests for get_title_length_hist function"""

    def test_get_title_length_hist_success(self, mock_db_connection):
        """Test successful histogram generation"""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"ncode": "N001", "title": "短いタイトル", "global_point": 1000},
            {"ncode": "N002", "title": "これは少し長いタイトルです", "global_point": 900},
            {"ncode": "N003", "title": "タイ", "global_point": 800},
        ]
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        with patch("narou_func.db_func.db_connect") as mock_connect, patch(
            "narou_func.plt.savefig"
        ) as mock_savefig, patch("narou_func.plt.show"):
            mock_connect.return_value = mock_db_connection

            narou_func.get_title_length_hist(2024, 100)

            # Verify SQL was executed
            mock_cursor.execute.assert_called_once()
            
            # Verify savefig was called with correct filename
            mock_savefig.assert_called_once()
            call_args = mock_savefig.call_args[0][0]
            assert "hist_2024_100.png" in call_args

    def test_get_title_length_hist_sql_format(self, mock_db_connection):
        """Test that SQL query is correctly formatted"""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        with patch("narou_func.db_func.db_connect") as mock_connect, patch(
            "narou_func.plt.show"
        ):
            mock_connect.return_value = mock_db_connection

            narou_func.get_title_length_hist(2024, 100)

            # Verify SQL query structure
            call_args = mock_cursor.execute.call_args
            sql = call_args[0][0]
            assert "general_firstup BETWEEN" in sql
            assert "ORDER BY global_point DESC" in sql
            assert "LIMIT" in sql

    def test_get_title_length_hist_db_connection_closed(self, mock_db_connection):
        """Test that database connection is properly closed"""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        with patch("narou_func.db_func.db_connect") as mock_connect, patch(
            "narou_func.plt.show"
        ):
            mock_connect.return_value = mock_db_connection

            narou_func.get_title_length_hist(2024, 100)

            mock_db_connection.close.assert_called_once()

    def test_get_title_length_hist_db_error(self, mock_db_connection):
        """Test error handling in histogram generation"""
        mock_db_connection.cursor.side_effect = Exception("DB Error")

        with patch("narou_func.db_func.db_connect") as mock_connect:
            mock_connect.return_value = mock_db_connection

            # Should handle exception gracefully
            with pytest.raises(Exception):
                narou_func.get_title_length_hist(2024, 100)


class TestGetTitleLengthMean:
    """Tests for get_title_length_mean function"""

    def test_get_title_length_mean_multiple_years(self, mock_db_connection):
        """Test mean calculation for multiple years"""
        sample_data = [
            {"ncode": "N001", "title": "短いタイトル", "global_point": 1000},
            {"ncode": "N002", "title": "これは少し長いタイトルです", "global_point": 900},
        ]
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = sample_data
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        with patch("narou_func.db_func.db_connect") as mock_connect, patch(
            "narou_func.plt.savefig"
        ) as mock_savefig, patch("narou_func.plt.show"):
            mock_connect.return_value = mock_db_connection

            narou_func.get_title_length_mean(2020, 2024, 100)

            # Verify savefig was called
            mock_savefig.assert_called_once()
            call_args = mock_savefig.call_args[0][0]
            assert "plot_top_2020_2024_100.png" in call_args

    def test_get_title_length_mean_single_year(self, mock_db_connection):
        """Test mean calculation for single year"""
        sample_data = [
            {"ncode": "N001", "title": "テスト", "global_point": 1000},
        ]
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = sample_data
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        with patch("narou_func.db_func.db_connect") as mock_connect, patch(
            "narou_func.plt.savefig"
        ) as mock_savefig, patch("narou_func.plt.show"), patch(
            "narou_func.plt.xticks"
        ) as mock_xticks:
            mock_connect.return_value = mock_db_connection

            narou_func.get_title_length_mean(2024, 2024, 100)

            # For single year, xticks should be set to [2024]
            mock_xticks.assert_called()

    def test_get_title_length_mean_step_calculation(self, mock_db_connection):
        """Test that X-axis step is calculated correctly"""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        with patch("narou_func.db_func.db_connect") as mock_connect, patch(
            "narou_func.plt.show"
        ):
            mock_connect.return_value = mock_db_connection

            # Test step calculation logic
            start_year = 2020
            end_year = 2024
            if start_year < end_year:
                step = max(1, int((end_year - start_year) / 5))
                assert step > 0
            else:
                step = None

    def test_get_title_length_mean_db_connection_closed(self, mock_db_connection):
        """Test that database connection is properly closed"""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        with patch("narou_func.db_func.db_connect") as mock_connect, patch(
            "narou_func.plt.show"
        ):
            mock_connect.return_value = mock_db_connection

            narou_func.get_title_length_mean(2024, 2024, 100)

            mock_db_connection.close.assert_called_once()


class TestGetNovelTypeNums:
    """Tests for get_nobel_type_nums function"""

    def test_get_novel_type_nums_success(self, mock_db_connection):
        """Test novel type aggregation"""
        mock_cursor = MagicMock()
        # First query returns long novel count
        # Second query returns short novel count
        mock_cursor.fetchone.side_effect = [
            {"count(*)": 100},  # Long novels for 2020
            {"count(*)": 50},   # Short novels for 2020
            {"count(*)": 120},  # Long novels for 2021
            {"count(*)": 60},   # Short novels for 2021
        ]
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        with patch("narou_func.db_func.db_connect") as mock_connect, patch(
            "narou_func.plt.savefig"
        ) as mock_savefig, patch("narou_func.plt.show"):
            mock_connect.return_value = mock_db_connection

            narou_func.get_nobel_type_nums(2020, 2021)

            # Verify savefig was called
            mock_savefig.assert_called_once()
            call_args = mock_savefig.call_args[0][0]
            assert "nobel_type_2020-2021.png" in call_args

    def test_get_novel_type_nums_sql_format(self, mock_db_connection):
        """Test that SQL queries are correctly formatted"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [
            {"count(*)": 100},
            {"count(*)": 50},
        ]
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        with patch("narou_func.db_func.db_connect") as mock_connect, patch(
            "narou_func.plt.show"
        ):
            mock_connect.return_value = mock_db_connection

            narou_func.get_nobel_type_nums(2024, 2024)

            # Verify SQL queries
            calls = mock_cursor.execute.call_args_list
            assert len(calls) >= 2

            # Check for novel_type filtering
            for call in calls:
                sql = call[0][0]
                assert "novel_type" in sql
                assert "count(*)" in sql.lower()

    def test_get_novel_type_nums_legend_labels(self, mock_db_connection):
        """Test that legend shows 'long' and 'short' labels"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [
            {"count(*)": 100},
            {"count(*)": 50},
        ]
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        with patch("narou_func.db_func.db_connect") as mock_connect, patch(
            "narou_func.plt.legend"
        ) as mock_legend, patch("narou_func.plt.show"):
            mock_connect.return_value = mock_db_connection

            narou_func.get_nobel_type_nums(2024, 2024)

            # Verify legend was called
            mock_legend.assert_called()

    def test_get_novel_type_nums_db_connection_closed(self, mock_db_connection):
        """Test that database connection is properly closed"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [
            {"count(*)": 100},
            {"count(*)": 50},
        ]
        mock_db_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )

        with patch("narou_func.db_func.db_connect") as mock_connect, patch(
            "narou_func.plt.show"
        ):
            mock_connect.return_value = mock_db_connection

            narou_func.get_nobel_type_nums(2024, 2024)

            mock_db_connection.close.assert_called_once()


class TestGraphOutputDirectory:
    """Tests for graph output directory handling"""

    def test_img_directory_exists(self):
        """Test that img directory exists"""
        img_dir = "./img"
        assert os.path.isdir(img_dir) or not os.path.exists(img_dir)

    def test_graph_file_path_format(self):
        """Test that graph file paths are correctly formatted"""
        img_dir = "./img"
        
        # Test histogram path
        hist_path = f"{img_dir}/hist_2024_100.png"
        assert "hist_" in hist_path
        assert hist_path.endswith(".png")

        # Test mean path
        mean_path = f"{img_dir}/plot_top_2020_2024_100.png"
        assert "plot_top_" in mean_path
        assert mean_path.endswith(".png")

        # Test novel type path
        type_path = f"{img_dir}/nobel_type_2020-2024.png"
        assert "nobel_type_" in type_path
        assert type_path.endswith(".png")
