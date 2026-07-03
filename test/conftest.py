"""
Pytest configuration and fixtures
"""

import pytest
import os
from unittest.mock import MagicMock, patch
import pymysql


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables for database connection"""
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "3306")
    monkeypatch.setenv("MYSQL_USER", "test_user")
    monkeypatch.setenv("MYSQL_PASSWORD", "test_password")
    monkeypatch.setenv("MYSQL_DATABASE", "test_db")


@pytest.fixture
def mock_db_connection():
    """Create a mock database connection"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=None)
    return mock_conn


@pytest.fixture
def sample_novel_data():
    """Sample novel data for testing"""
    return {
        "0": {
            "ncode": "N0001",
            "title": "Test Novel 1",
            "userid": 1,
            "writer": "Test Author",
            "story": "Test story",
            "biggenre": 1,
            "genre": 101,
            "gensaku": 0,
            "keyword": "test",
            "general_firstup": "2024-01-01 12:00:00",
            "general_lastup": "2024-01-01 12:00:00",
            "novel_type": 1,
            "end": 0,
            "general_all_no": 10,
            "length": 50000,
            "time": 100,
            "isstop": 0,
            "isr15": 0,
            "isbl": 0,
            "isgl": 0,
            "iszankoku": 0,
            "istensei": 0,
            "istenni": 0,
            "global_point": 1000,
            "daily_point": 100,
            "weekly_point": 200,
            "monthly_point": 300,
            "quarter_point": 400,
            "yearly_point": 500,
            "fav_novel_cnt": 50,
            "impression_cnt": 10,
            "review_cnt": 5,
            "all_point": 600,
            "all_hyoka_cnt": 100,
            "sasie_cnt": 0,
            "kaiwaritu": "0%",
            "novelupdated_at": "2024-01-01 12:00:00",
            "updated_at": "2024-01-01 12:00:00",
        }
    }


@pytest.fixture
def sample_api_response():
    """Sample API response data"""
    return [
        {"allcount": 500},  # allcount in first element
        {
            "ncode": "N0001",
            "title": "テスト小説1",
            "userid": 1,
            "writer": "テスト作者",
            "story": "テストストーリー",
            "biggenre": 1,
            "genre": 101,
            "gensaku": 0,
            "keyword": "テスト",
            "general_firstup": "2024-01-01 12:00:00",
            "general_lastup": "2024-01-02 12:00:00",
            "novel_type": 1,
            "end": 0,
            "general_all_no": 10,
            "length": 50000,
            "time": 100,
            "isstop": 0,
            "isr15": 0,
            "isbl": 0,
            "isgl": 0,
            "iszankoku": 0,
            "istensei": 0,
            "istenni": 0,
            "global_point": 1000,
            "daily_point": 100,
            "weekly_point": 200,
            "monthly_point": 300,
            "quarter_point": 400,
            "yearly_point": 500,
            "fav_novel_cnt": 50,
            "impression_cnt": 10,
            "review_cnt": 5,
            "all_point": 600,
            "all_hyoka_cnt": 100,
            "sasie_cnt": 0,
            "kaiwaritu": "0%",
            "novelupdated_at": "2024-01-02 12:00:00",
            "updated_at": "2024-01-02 12:00:00",
        },
    ]
