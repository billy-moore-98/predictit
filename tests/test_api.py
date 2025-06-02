import pytest
import requests

from botocore.exceptions import ClientError
from src.api import PredictitAPI
from unittest.mock import patch, MagicMock

@patch('src.api.requests.get')
def test_poll_market_data_all(mock_get):
    mock_response = mock_get.return_value
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {'markets': []}
    api = PredictitAPI()
    result = api.poll_market_data()
    assert result == {'markets': []}
    mock_get.assert_called_once_with('https://www.predictit.org/api/marketdata/all')

@patch('src.api.requests.get')
def test_poll_market_data_id(mock_get):
    market_id = '12345'
    mock_response = mock_get.return_value
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {'market': {'id': market_id}}
    api = PredictitAPI()
    result = api.poll_market_data(market_id=market_id)
    assert result == {'market': {'id': market_id}}
    mock_get.assert_called_once_with(f'https://www.predictit.org/api/marketdata/markets/{market_id}')

@patch('src.api.requests.get')
def test_poll_market_http_error(mock_get, caplog):
    mock_get.side_effect = requests.exceptions.HTTPError("500 server error")
    api = PredictitAPI()
    with caplog.at_level("ERROR"):
        result = api.poll_market_data()
    assert result is None
    assert "HTTP error occurred" in caplog.text

@patch('src.api.boto3.client')
def test_store_to_s3_success(mock_boto_client):
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3
    test_bucket = 'test-bucket'
    test_filename = 'test_file.json'
    test_data = {'markets': []}
    predictit = PredictitAPI()
    expected_key = f'predictit/stage/{test_filename}'
    predictit.store_to_s3(test_data, bucket=test_bucket, filename=test_filename)
    mock_s3.put_object.assert_called_once_with(
        Bucket=test_bucket,
        Key=expected_key,
        Body='{"markets": []}',
        ContentType='application/json'
    )

@patch('src.api.boto3.client')
def test_store_to_s3_failure(mock_boto_client):
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3
    mock_s3.put_object.side_effect = ClientError(
        error_response={
            'Error': {
                'Code': 'AccessDenied',
                'Message': 'Access Denied'
            }
        },
        operation_name='PutObject'
    )
    test_data = {'markets': []}
    test_bucket = 'test-bucket'
    test_filename = 'test_file.json'
    predictit = PredictitAPI()
    with pytest.raises(ClientError):
        predictit.store_to_s3(test_data, bucket=test_bucket, filename=test_filename)
    
    mock_s3.put_object.assert_called_once_with(
        Bucket=test_bucket,
        Key=f'predictit/stage/{test_filename}',
        Body='{"markets": []}',
        ContentType='application/json'
    )