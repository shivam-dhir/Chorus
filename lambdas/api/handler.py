import json
import logging
import os
import time

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ.get("WORKFLOWS_TABLE", "workflows")
table = dynamodb.Table(TABLE_NAME)


def handler(event, context):
    logger.info("Create workflow request received")
    logger.info("Raw event:")
    logger.info(json.dumps(event))

    try:
        # Handle both proxy and non-proxy payloads
        if "body" in event and event["body"] is not None:
            body = json.loads(event["body"])
        else:
            body = event  # API Gateway test / mapped request

        workflow_id = body["workflow_id"]
        definition = body["definition"]

        table.put_item(
            Item={
                "workflow_id": workflow_id,
                "definition": definition,
                "created_at": int(time.time()),
                "version": 1
            }
        )

        return {
            "statusCode": 201,
            "body": json.dumps({
                "message": "Workflow created",
                "workflow_id": workflow_id
            })
        }

    except Exception as e:
        logger.error("Failed to create workflow")
        logger.error(str(e))

        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "Invalid workflow payload"
            })
        }


