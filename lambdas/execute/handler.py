import json
import time
import uuid
import os
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
sqs = boto3.client("sqs")

WORKFLOWS_TABLE = os.environ.get("WORKFLOWS_TABLE", "workflows")
EXECUTIONS_TABLE = os.environ.get("EXECUTIONS_TABLE", "workflow_executions")
STEPS_QUEUE_URL = os.environ["STEPS_QUEUE_URL"]

workflows_table = dynamodb.Table(WORKFLOWS_TABLE)
executions_table = dynamodb.Table(EXECUTIONS_TABLE)


def handler(event, context):
    workflow_id = event["pathParameters"]["workflow_id"]

    # 1️ Fetch workflow definition
    workflow = workflows_table.get_item(
        Key={"workflow_id": workflow_id}
    ).get("Item")

    if not workflow:
        return response(404, {"error": "Workflow not found"})

    steps = workflow["definition"]["steps"]

    # 2️ Create execution record
    execution_id = str(uuid.uuid4())
    now = int(time.time())

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

    logger.info("Workflow execution state written to DynamoDB")

    # 3️ Enqueue first step
    first_step = steps[0]

    sqs.send_message(
        QueueUrl=STEPS_QUEUE_URL,
        MessageBody=json.dumps({
            "workflow_id": workflow_id,
            "execution_id": execution_id,
            "step_index": 0,
            "step": first_step
        })
    )

    logger.info("First step enqueued to SQS")

    # 4 Return immediately
    return response(200, {
        "workflow_id": workflow_id,
        "execution_id": execution_id,
        "status": "RUNNING"
    })


def response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }
