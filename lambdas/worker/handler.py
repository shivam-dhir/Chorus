import json
import logging
import os
import time

import boto3
from botocore.exceptions import ClientError

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
    for record in event["Records"]:
        process_message(record)


def process_message(record):
    message = json.loads(record["body"])

    workflow_id = message["workflow_id"]
    execution_id = message["execution_id"]
    step_index = message["step_index"]
    step = message["step"]

    logger.info(
        f"Executing step {step_index} for execution {execution_id}"
    )

    try:
        # Execute the step
        execute_step(step)

        # Update execution progress
        update_execution_state(
            workflow_id,
            execution_id,
            step_index + 1,
            "RUNNING"
        )

        # Fetch workflow definition
        workflow = workflows_table.get_item(
            Key={"workflow_id": workflow_id}
        )["Item"]

        steps = workflow["definition"]["steps"]

        # Enqueue next step or complete execution
        if step_index + 1 < len(steps):
            enqueue_next_step(
                workflow_id,
                execution_id,
                step_index + 1,
                steps[step_index + 1]
            )
        else:
            mark_execution_completed(
                workflow_id,
                execution_id
            )

    except Exception as e:
        logger.error(str(e))
        mark_execution_failed(
            workflow_id,
            execution_id,
            str(e)
        )
        raise  # let SQS retry


# -------------------------
# Step execution
# -------------------------

def execute_step(step):
    step_type = step["type"]

    if step_type == "log":
        logger.info(step["message"])
        time.sleep(0.2)  # simulate work
    else:
        raise ValueError(f"Unknown step type: {step_type}")


# -------------------------
# DynamoDB updates
# -------------------------

def update_execution_state(workflow_id, execution_id, next_step, status):
    executions_table.update_item(
        Key={
            "workflow_id": workflow_id,
            "execution_id": execution_id
        },
        UpdateExpression="""
            SET #s = :s,
                current_step = :cs,
                updated_at = :u
        """,
        ExpressionAttributeNames={
            "#s": "status"
        },
        ExpressionAttributeValues={
            ":s": status,
            ":cs": next_step,
            ":u": int(time.time())
        }
    )


def mark_execution_completed(workflow_id, execution_id):
    executions_table.update_item(
        Key={
            "workflow_id": workflow_id,
            "execution_id": execution_id
        },
        UpdateExpression="""
            SET #s = :s,
                completed_at = :c
        """,
        ExpressionAttributeNames={
            "#s": "status"
        },
        ExpressionAttributeValues={
            ":s": "COMPLETED",
            ":c": int(time.time())
        }
    )


def mark_execution_failed(workflow_id, execution_id, error):
    executions_table.update_item(
        Key={
            "workflow_id": workflow_id,
            "execution_id": execution_id
        },
        UpdateExpression="""
            SET #s = :s,
                error = :e,
                updated_at = :u
        """,
        ExpressionAttributeNames={
            "#s": "status"
        },
        ExpressionAttributeValues={
            ":s": "FAILED",
            ":e": error,
            ":u": int(time.time())
        }
    )


# -------------------------
# SQS enqueue
# -------------------------

def enqueue_next_step(workflow_id, execution_id, step_index, step):
    sqs.send_message(
        QueueUrl=STEPS_QUEUE_URL,
        MessageBody=json.dumps({
            "workflow_id": workflow_id,
            "execution_id": execution_id,
            "step_index": step_index,
            "step": step
        })
    )
