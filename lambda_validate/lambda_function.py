import boto3
import json
import logging
import os

from src.validate import PredictitResponse
from typing import Optional

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')

def lambda_function(execution_timestamp: str):
    """
    Lambda function to validate the PredictIt API data stored in S3

    Params:
        execution_timestamp (str): The execution timestamp for the data
    """
    # Validate the PredictIt API data
    logger.info('Validating PredictIt API data now')
    bucket = os.getenv('S3_BUCKET')
    if not bucket:
        raise ValueError("S3_BUCKET environment variable is not set")
    
    # Load the data from S3
    s3_object = s3_client.get_object(Bucket=bucket, Key=f'predictit/stage/market_data_{execution_timestamp}.json')
    data = json.loads(s3_object['Body'].read())
    
    try:
        # Validate the data
        PredictitResponse(data)
    except Exception as e:
        logger.error(f'Error occurred during data validation: {e}')
        raise
    logger.info('Successfully validated data')

def lambda_handler(event, context) -> Optional[dict]:
    """
    Lambda handler to validate the PredictIt API data stored in S3

    Params:
        event (dict): The event data passed to the Lambda function
        context (LambdaContext): The context object passed to the Lambda function
    Returns:
        Dict status message
    """
    try:
        execution_timestamp = event.get('execution_timestamp')
        lambda_function(execution_timestamp)
        return {
            'StatusCode': 200,
            'message': 'PredictAPI data successfully validated'
        }
    except Exception as e:
        logger.error(f'Error occurred: {e}')
        raise
