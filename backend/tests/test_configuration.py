import os
import unittest
from unittest.mock import patch

from app import config


class ConfigurationTests(unittest.TestCase):
    def test_database_url_comes_from_environment(self):
        with patch.dict(
            os.environ,
            {"APP_ENV": "production", "DATABASE_URL": "sqlite:///configured.db"},
            clear=False,
        ):
            self.assertEqual(config.get_database_url(), "sqlite:///configured.db")

    def test_production_rejects_missing_or_placeholder_jwt_secret(self):
        for value in ("", "change-this-to-a-long-random-secret-key"):
            with self.subTest(value=value), patch.dict(
                os.environ,
                {"APP_ENV": "production", "JWT_SECRET_KEY": value},
                clear=False,
            ):
                with self.assertRaises(RuntimeError):
                    config.get_jwt_secret()

    def test_production_accepts_valid_configuration(self):
        with patch.dict(
            os.environ,
            {
                "APP_ENV": "production",
                "DATABASE_URL": "sqlite:///configured.db",
                "JWT_SECRET_KEY": "a-real-test-secret-that-is-not-a-placeholder",
            },
            clear=False,
        ):
            config.validate_configuration()
            self.assertEqual(config.get_jwt_secret(), os.environ["JWT_SECRET_KEY"])

    def test_missing_database_url_is_rejected_in_all_environments(self):
        with patch.dict(os.environ, {"APP_ENV": "development"}, clear=True):
            with self.assertRaises(RuntimeError):
                config.get_database_url()
            self.assertEqual(
                config.get_jwt_secret(), "development-only-secret-change-me"
            )
