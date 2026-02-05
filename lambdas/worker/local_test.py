from handler import handler

if __name__ == "__main__":
    test_event = {
        "workflow_id": "wf-local-test",
        "execution_id": "exec-123"
    }

    result = handler(test_event, None)
    print("Lambda result:")
    print(result)
