import boto3
import logging
import os

from src.api import PredictitAPI
from typing import Optional

logger = logging.getLogger()
logger.setLevel(logging.INFO)

predictit = PredictitAPI()
s3_client = boto3.client('s3')

def lambda_function(filename: str) -> None:
    """
    Lambda function to poll the predictit API and store the data in S3
    Params:
        excution_timestamp (str): The execution timestamp for the data
    """
    # Poll the PredictIt API
    logger.info('Polling PredictIt API market data now')
    data = predictit.poll_market_data()
    logger.info('Successfully polled API')
    logger.info('Storing to S3 now')
    bucket = os.getenv('S3_BUCKET')
    if not bucket:
        raise ValueError("S3_BUCKET environment variable is not set")
    predictit.store_to_s3(data, bucket=bucket, filename=filename)
    logging.info('Successfully stored data to S3')


def lambda_handler(event, context) -> Optional[dict]:
    """
    Lambda handler to poll the PredictIt API and store the data in S3

    Params:
        event (dict): The event data passed to the Lambda function
        context (LambdaContext): The context object passed to the Lambda function
    Returns:
        Dict status message
    """
    try:
        filename = event.get('filename')
        lambda_function(filename)
        return {
            'StatusCode': 200,
            'message': 'PredictAPI data succcessfully polled and stored to S3'
        }
    except Exception as e:
        logger.error(f'Error occurred: {e}')
        raise