import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")

EXECUTIONS_TABLE = os.environ.get("EXECUTIONS_TABLE", "workflow_executions")
table = dynamodb.Table(EXECUTIONS_TABLE)


def handler(event, context):
    logger.info("Get execution status request")
    logger.info(json.dumps(event))

    try:
        path = event["pathParameters"]
        workflow_id = path["workflow_id"]
        execution_id = path["execution_id"]

        resp = table.get_item(
            Key={
                "workflow_id": workflow_id,
                "execution_id": execution_id
            }
        )

        if "Item" not in resp:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Execution not found"})
            }

        return {
            "statusCode": 200,
            "body": json.dumps(resp["Item"])
        }

    except ClientError as e:
        logger.error(str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to fetch execution"})
        }

    except Exception as e:
        logger.error(str(e))
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid request"})
        }
