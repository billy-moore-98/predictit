import pytest
import requests

from src.api import PredictitAPI
from unittest.mock import patch

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