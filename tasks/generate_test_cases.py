from Generative_ai.celery_config  import celery_app

@celery_app.task(name="tasks.generate_test_cases")
def generate_test_cases(input_data):
    # Placeholder logic (replace with GenAI logic)
    return {"status": "success", "test_cases": ["test1", "test2"]}
