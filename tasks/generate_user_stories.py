from Generative_ai.celery_config  import celery_app

@celery_app.task(name="tasks.generate_user_stories")
def generate_user_stories(input_text):
    # Placeholder logic
    return {
        "status": "success",
        "user_stories": [
            "As a user, I want to log in so that I can access my dashboard.",
            "As an admin, I want to view reports so I can make data-driven decisions."
        ]
    }
