import asyncio
import ssl
import unittest
import pytest
# # Uncomment for tests
# from unittest.mock import patch, Mock
# import requests

from eits_python_api.base import AsyncAPIBase


@pytest.fixture
def example_url():
    return "https://example.com"


class TestBaseInit(unittest.TestCase):
    def test_init_url(self):
        base = AsyncAPIBase(example_url)
        self.assertIsInstance(base, AsyncAPIBase)
        self.assertTrue(hasattr(base, "url"))
        self.assertEqual(base.url, example_url)

    def test_init_verify_false(self):
        base = AsyncAPIBase(example_url, verify=False)
        self.assertTrue(hasattr(base, "ssl_context"))
        self.assertIsInstance(base.ssl_context, ssl.SSLContext)
        self.assertEqual(base.ssl_context.check_hostname, False)

    def test_init_limit(self):
        base = AsyncAPIBase(example_url, limit=10)
        self.assertTrue(hasattr(base, "limit"))
        self.assertIsInstance(base.limit, asyncio.Semaphore)
        self.assertEqual(base.limit._value, 10)

    def test_init_headers(self):
        base = AsyncAPIBase(example_url)
        self.assertTrue(hasattr(base, "headers"))
        self.assertIsInstance(base.headers, dict)
        self.assertEqual(base.headers, {"accept": "application/json"})

# TODO: Write tests for AsyncAPIBase sync method
# class TestBaseSynchronousMethods(unittest.TestCase):
#     @patch("requests.Session")
#     def test_get_sync_success(self, mock_session):
#         json_response = {"key": "value"}

#         response = Mock()
#         response.raise_for_status.side_effect = None
#         response.json.return_value = json_response

#         session = mock_session.return_value
#         session.get.return_value = response

#         base = AsyncAPIBase(url=example_url)
#         result = base.get_sync()

#         # Assert that the method returns the expected JSON payload
#         self.assertEqual(result, json_response)

#     @patch("requests.Session")
#     def test_get_sync_error(self, mock_session):
#         # Create a mock response with an error (e.g. 404)
#         response = Mock()
#         response.raise_for_status.side_effect = (
#             requests.exceptions.RequestException()
#         )

#         # Create a mock session object
#         session = mock_session.return_value
#         session.get.return_value = response

#         # Call the get_sync method
#         base = AsyncAPIBase(url="https://example.com")
#         result = base.get_sync()

#         # Assert that the method returns None when an error occurs
#         self.assertIsNone(result)

#     @patch("requests.Session")
#     def test_get_sync_timeout(self, mock_session):
#         # Create a mock response with a timeout error
#         response = Mock()
#         response.raise_for_status.side_effect = requests.exceptions.Timeout()

#         # Create a mock session object
#         session = mock_session.return_value
#         session.get.return_value = response

#         # Call the get_sync method
#         base = AsyncAPIBase(url="https://example.com")
#         result = base.get_sync()

#         # Assert that the method returns None when a timeout occurs
#         self.assertIsNone(result)
