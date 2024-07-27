import pytest
import csv
from unittest.mock import patch
from eits_python_api.common import save_csv


def test_save_csv_success(data, tmp_path):
    # Mock data
    filename = tmp_path / "test.csv"

    # Call the function
    save_csv(data, str(filename))

    # Assert logging message (indirectly through patching)
    with patch("logging.info") as mock_info:
        mock_info.assert_called_once_with(f"Saving CSV output to {filename}")

    # Assert file content
    with open(filename, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        assert next(reader) == list(data[0].keys())  # Check header row
        assert list(reader) == data


@pytest.fixture
def data():
    return [{"col1": "value1", "col2": 10}]


def test_save_csv_empty_data(tmp_path):
    # Empty data
    filename = tmp_path / "test.csv"

    # Assert no file is created
    with pytest.raises(FileNotFoundError):
        save_csv([], str(filename))


def test_save_csv_exception(tmp_path, mocker):
    # Mock exception during writing
    mocker.patch("csv.DictWriter", side_effect=Exception("Write error"))
    data = [{"col1": "value1", "col2": 10}]
    filename = tmp_path / "test.csv"

    # Assert exception is raised
    with pytest.raises(Exception):
        save_csv(data, str(filename))
