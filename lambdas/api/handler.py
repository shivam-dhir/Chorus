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
    logger.info(json.dumps(event))

    try:
        body = json.loads(event["body"])
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
        logger.error(str(e))
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "Invalid workflow payload"
            })
        }
