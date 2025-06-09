import pytest

from lambda_fetch.lambda_function import lambda_function, lambda_handler
from unittest.mock import patch


@patch("lambda_fetch.lambda_function.lambda_function")
def test_lambda_handler_success(mock_lambda_func):
    event = {"filename": "test_data.json"}
    response = lambda_handler(event, None)
    mock_lambda_func.assert_called_once_with("test_data.json")
    assert response == {
        "StatusCode": 200,
        "message": "PredictAPI data succcessfully polled and stored to S3",
    }


@patch("lambda_fetch.lambda_function.lambda_function")
def test_lambda_handler_no_filename(mock_lambda_func):
    event = {}
    with pytest.raises(ValueError, match="Filename must be provided in the event data"):
        lambda_handler(event, None)


@patch("lambda_fetch.lambda_function.os.getenv")
@patch("lambda_fetch.lambda_function.predictit")
@patch("lambda_fetch.lambda_function.s3_client")
def test_lambda_function_success(mock_s3_client, mock_predictit, mock_getenv):
    mock_getenv.return_value = "fake-bucket"
    mock_predictit.poll_market_data.return_value = {"markets": []}

    lambda_function("test.json")

    mock_predictit.poll_market_data.assert_called_once()
    mock_predictit.store_to_s3.assert_called_once_with(
        mock_s3_client, {"markets": []}, bucket="fake-bucket", filename="test.json"
    )


@patch("lambda_fetch.lambda_function.os.getenv", return_value=None)
def test_lambda_function_no_s3_bucket(mock_getenv):
    with pytest.raises(ValueError, match="S3_BUCKET environment variable is not set"):
        lambda_function("test_data.json")
