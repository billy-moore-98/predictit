import boto3
import json
import logging
import os

from src.api import PredictitAPI
from typing import Optional

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")


def lambda_function(filename: str):
    """
    Lambda function to validate the PredictIt API data stored in S3

    Params:
        execution_timestamp (str): The execution timestamp for the data
    """
    # Validate the PredictIt API data
    logger.info("Validating PredictIt API data now")
    bucket = os.getenv("S3_BUCKET")
    if not bucket:
        raise ValueError("S3_BUCKET environment variable is not set")
    source_key = f"predictit/stage/{filename}"
    destination_key = f"predictit/raw_data/{filename}"
    # Load the data from S3
    s3_object = s3_client.get_object(Bucket=bucket, Key=source_key)
    data = json.loads(s3_object["Body"].read())

    try:
        # Validate the data
        predictit = PredictitAPI()
        predictit.validate(data)
        logger.info("Successfully validated data")
    except Exception as e:
        logger.error(f"Error occurred during data validation: {e}")
        raise

    # copy to raw data and delete stage data
    s3_client.copy_object(
        Bucket=bucket,
        CopySource={"Bucket": bucket, "Key": source_key},
        Key=destination_key,
    )
    s3_client.delete_object(Bucket=bucket, Key=source_key)


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
        filename = event.get("filename")
        if not filename:
            raise ValueError("Filename must be provided in the event data")
        lambda_function(filename)
        return {"StatusCode": 200, "message": "PredictAPI data successfully validated"}
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise
