import json
import logging
import os
import time
import uuid

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB setup (outside handler = reused across invocations)
dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ.get("WORKFLOW_TABLE", "workflow_executions")
table = dynamodb.Table(TABLE_NAME)


def handler(event, context):
    """
    Chorus worker Lambda.
    Creates or updates a workflow execution record.
    """

    logger.info("Chorus worker invoked")
    logger.info(f"Event: {json.dumps(event)}")

    workflow_id = event.get("workflow_id", "wf-test")
    execution_id = event.get("execution_id", str(uuid.uuid4()))

    try:
        table.put_item(
            Item={
                "workflow_id": workflow_id,
                "execution_id": execution_id,
                "status": "RUNNING",
                "current_step": 0,
                "updated_at": int(time.time())
            }
        )

        logger.info("Workflow execution state written to DynamoDB")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Workflow execution recorded",
                "workflow_id": workflow_id,
                "execution_id": execution_id
            })
        }

    except ClientError as e:
        logger.error(f"DynamoDB error: {e}")

        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Failed to write workflow execution"
            })
        }
