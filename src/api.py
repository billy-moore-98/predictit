import logging
import requests

from typing import Optional

from .validate import PredictitResponse

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PredictitAPI:
    def __init__(self, base_url="https://www.predictit.org/api/marketdata"):
        self.base_url = base_url

    def poll_market_data(self, market_id: Optional[str] = None) -> Optional[dict]:
        """
        Poll the PredictIt api market data and return the latest share prices

        Args:
            market_id(str, optional): The market id to fetch, if None then fetch all markets
        Returns:
            dict: The JSON response
        """
        if market_id:
            url = f"{self.base_url}/markets/{market_id}"
        else:
            url = f"{self.base_url}/all"
        try:
            response = requests.get(url)
            response.raise_for_status()
            json_data = response.json()
            return json_data
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error occurred: {e}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")

    def validate(self, response: dict) -> bool:
        logger.info("Validating PredictIt response now")
        try:
            PredictitResponse(**response)
            logger.info("Validated successfully")
            return True
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise
