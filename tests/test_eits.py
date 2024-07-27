import unittest
import pytest


@pytest.fixture
def example_url():
    return "https://example.com"


class TestInit(unittest.TestCase):
    pass
