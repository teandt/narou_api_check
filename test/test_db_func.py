"""
Tests for db_func module
"""

import pytest
import os
import pymysql
import importlib
from unittest.mock import MagicMock, patch
import sys

# Add parent directory to path to import db_func
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db_func


class TestDbConnect:
    """Tests for db_connect function"""

    def test_db_connect_success_with_env(self, mock_env):
        """Test successful database connection with environment variables"""
        with patch("db_func.pymysql.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn

            result = db_func.db_connect()

            assert result == mock_conn
            mock_connect.assert_called_once()
            call_kwargs = mock_connect.call_args[1]
            assert call_kwargs["host"] == "localhost"
            assert call_kwargs["port"] == 3306
            assert call_kwargs["user"] == "test_user"
            assert call_kwargs["password"] == "test_password"
            assert call_kwargs["database"] == "test_db"
            assert call_kwargs["charset"] == "utf8mb4"

    def test_db_connect_charset_utf8mb4(self, mock_env):
        """Test that connection is set to utf8mb4 charset"""
        with patch("db_func.pymysql.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn

            db_func.db_connect()

            call_kwargs = mock_connect.call_args[1]
            assert call_kwargs["charset"] == "utf8mb4"

    def test_db_connect_uses_dict_cursor(self, mock_env):
        """Test that connection uses DictCursor"""
        with patch("db_func.pymysql.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn

            db_func.db_connect()

            call_kwargs = mock_connect.call_args[1]
            assert (
                call_kwargs["cursorclass"]
                == __import__("pymysql.cursors", fromlist=["DictCursor"]).DictCursor
            )

    def test_db_connect_invalid_port(self, mock_env, monkeypatch):
        """Test that invalid port raises ValueError"""
        monkeypatch.setenv("DB_PORT", "invalid_port")

        with pytest.raises(ValueError):
            db_func.db_connect()

    def test_db_connect_connection_error(self, mock_env):
        """Test connection error handling"""
        with patch("db_func.pymysql.connect") as mock_connect:
            mock_connect.side_effect = pymysql.OperationalError("Connection refused")

            with pytest.raises(pymysql.OperationalError):
                db_func.db_connect()

    def test_db_connect_loads_env_file(self, mock_env, monkeypatch):
        """Test that .env file is loaded"""
        with patch("dotenv.load_dotenv") as mock_load_dotenv:
            importlib.reload(db_func)

            mock_load_dotenv.assert_called_once_with(".env")

        importlib.reload(db_func)
