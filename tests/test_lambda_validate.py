import json
import pytest

from lambda_validate.lambda_function import lambda_function, lambda_handler
from unittest.mock import patch, MagicMock


@patch("lambda_validate.lambda_function.lambda_function")
def test_lambda_handler_success(mock_lambda_func):
    event = {"filename": "test_filename.json"}
    response = lambda_handler(event, None)
    mock_lambda_func.assert_called_once_with("test_filename.json")
    assert response == {
        "StatusCode": 200,
        "message": "PredictAPI data successfully validated",
    }


@patch("lambda_validate.lambda_function.lambda_function")
def test_lambda_handler_no_filename(mock_lambda_func):
    event = {}
    with pytest.raises(ValueError, match="Filename must be provided in the event data"):
        lambda_handler(event, None)


@patch("lambda_validate.lambda_function.os.getenv", return_value=None)
def test_lambda_function_no_s3_bucket(mock_getenv):
    with pytest.raises(ValueError, match="S3_BUCKET environment variable is not set"):
        lambda_function("test_filename.json")


@patch("lambda_validate.lambda_function.os.getenv", return_value="fake-bucket")
@patch("lambda_validate.lambda_function.s3_client")
@patch("lambda_validate.lambda_function.PredictitResponse")
def test_lambda_function_success(mock_predictit_response, mock_s3_client, mock_getenv):
    test_filename = "test_filename.json"
    test_data = {
        "markets": [
            {
                "id": 1,
                "name": "Test Market",
                "image": "test_image.png",
                "url": "http://example.com",
                "contracts": [
                    {
                        "id": 1,
                        "dateEnd": "2025-01-01T12:00:00Z",
                        "image": "contract_image.png",
                        "name": "Test Contract",
                        "shortName": "TC1",
                        "status": "open",
                        "lastTradePrice": 1.0,
                        "bestBuyYesCost": 0.5,
                        "bestBuyNoCost": 0.5,
                        "bestSellYesCost": 0.6,
                        "bestSellNoCost": 0.4,
                        "lastClosePrice": 1.0,
                        "displayOrder": 1.0,
                    }
                ],
                "timeStamp": test_filename,
                "status": "active",
            }
        ]
    }
    mock_json_body = MagicMock()
    mock_json_body.read.return_value = json.dumps(test_data).encode("utf-8")
    mock_s3_client.get_object.return_value = {"Body": mock_json_body}

    lambda_function(test_filename)

    mock_getenv.assert_called_once_with("S3_BUCKET")
    mock_s3_client.get_object.assert_called_once_with(
        Bucket="fake-bucket",
        Key=f"predictit/stage/{test_filename}",
    )
    mock_predictit_response.assert_called_once_with(**test_data)
    mock_s3_client.copy_object.assert_called_once_with(
        Bucket="fake-bucket",
        CopySource={
            "Bucket": "fake-bucket",
            "Key": f"predictit/stage/{test_filename}",
        },
        Key=f"predictit/raw_data/{test_filename}",
    )
    mock_s3_client.delete_object.assert_called_once_with(
        Bucket="fake-bucket",
        Key=f"predictit/stage/{test_filename}",
    )
