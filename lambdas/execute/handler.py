import json
import logging
import os
import time
import uuid

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")

WORKFLOWS_TABLE = os.environ.get("WORKFLOWS_TABLE", "workflows")
EXECUTIONS_TABLE = os.environ.get("EXECUTIONS_TABLE", "workflow_executions")

workflows_table = dynamodb.Table(WORKFLOWS_TABLE)
executions_table = dynamodb.Table(EXECUTIONS_TABLE)


def handler(event, context):
    logger.info("Execute workflow request received")
    logger.info(json.dumps(event))

    try:
        # Path parameter
        workflow_id = event["pathParameters"]["workflow_id"]

        # Fetch workflow definition
        workflow_resp = workflows_table.get_item(
            Key={"workflow_id": workflow_id}
        )

        if "Item" not in workflow_resp:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Workflow not found"})
            }

        workflow = workflow_resp["Item"]

        execution_id = str(uuid.uuid4())
        now = int(time.time())

        # Initialize execution state
        executions_table.put_item(
            Item={
                "workflow_id": workflow_id,
                "execution_id": execution_id,
                "status": "RUNNING",
                "current_step": 0,
                "started_at": now,
                "updated_at": now
            }
        )

        logger.info(f"Execution started: {execution_id}")

        return {
            "statusCode": 201,
            "body": json.dumps({
                "workflow_id": workflow_id,
                "execution_id": execution_id,
                "status": "RUNNING"
            })
        }

    except ClientError as e:
        logger.error(str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to start execution"})
        }

    except Exception as e:
        logger.error(str(e))
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid request"})
        }
