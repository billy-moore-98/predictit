import boto3
import datetime
import json
import requests

from botocore.exceptions import ClientError
from typing import Optional

class PredictitAPI:

    def __init__(self, base_url="https://www.predictit.org/api/marketdata"):
        self.base_url = base_url
        self.s3_client = boto3.client('s3')

    def poll_market_data(self, market_id: Optional[str] = None):
        """
        Poll the PredictIt api market data and return the latest share prices

        Args:
            market_id(str, optional): The market id to fetch, if None then fetch all markets
        Returns:
            dict: The JSON response
        """
        if market_id:
            url = f"{self.base_url}/marketdata/markets/{market_id}"
        else:
            url = f"{self.base_url}/all"
        try:
            response = requests.get(url)
            response.raise_for_status()
            json_data = response.json()
            return json_data
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Request exception: {e}")
        except Exception as e:
            print(f"Unknown error occurred: {e}")

    def store_to_s3(self, data: dict, bucket: Optional[str] = None, filename: Optional[str] = None):
        if not filename:
            timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%S')
            filename = f'market_data_{timestamp}.json'
        key = f'predictit/{filename}'
        try:
            self.s3_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=json.dumps(data),
                ContentType='application/json'
            )
            print(f'Uploaded {key} to S3 bucket {bucket}')
        except ClientError as e:
            print('Failed to upload to bucket: {e}')