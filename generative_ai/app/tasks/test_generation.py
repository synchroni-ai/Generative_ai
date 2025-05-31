from app.tasks.celery_worker import celery_app


@celery_app.task(bind=True, name="task_with_api_key.process_and_generate_task_multi")
def process_and_generate_task(
    self, file_paths, model_name, chunk_size, api_key, test_case_types, document_ids
):
    print(f"🎯 Celery task started for {len(file_paths)} files ({test_case_types})")
    task_id = self.request.id

    try:
        if model_name not in MODEL_DISPATCHER:
            raise HTTPException(
                status_code=400, detail=f"Unsupported model: {model_name}"
            )

        generation_function = MODEL_DISPATCHER[model_name]
        overall_results = []

        for idx, file_path in enumerate(file_paths):
            document_id = document_ids[idx]
            base_stem = Path(file_path).stem

            print(f"📄 Processing file: {base_stem}")
            chunks, cleaned_text = process_document(file_path, model_name, chunk_size)

            all_results = []
            all_combined_test_cases = ""
            test_cases_by_type = {}

            # MongoDB init for this document
            try:
                collection.update_one(
                    {"_id": ObjectId(document_id)},
                    {"$set": {"status": 0, "progress": []}},
                )
            except Exception as e:
                print("MongoDB update error (init):", str(e))

            for test_case_type in test_case_types:
                prompt_dir = Path("utils/prompts")
                prompt_path = prompt_dir / f"{test_case_type}.txt"

                if not prompt_path.exists():
                    raise HTTPException(
                        status_code=500,
                        detail=f"Prompt file not found: {prompt_path}",
                    )

                with open(prompt_path, "r") as f:
                    test_case_prompt = f.read()

                all_test_cases = []
                test_case_tokens = 0

                for chunk_index, chunk_text in enumerate(chunks, start=1):
                    try:
                        test_case_text, tokens = test_case_utils.generate_test_cases(
                            chunk_text,
                            generation_function,
                            test_case_prompt=test_case_prompt,
                        )
                        if test_case_text:
                            all_test_cases.append(test_case_text)
                            test_case_tokens += tokens
                    except Exception as e:
                        print(
                            f"Error generating test cases for chunk {chunk_index} ({test_case_type}): {e}"
                        )
                        continue

                combined_test_cases = "\n".join(all_test_cases)
                all_combined_test_cases += f"\n\n### {test_case_type.upper()} TEST CASES ###\n\n{combined_test_cases}"

                embedded_id = str(uuid.uuid4())
                test_cases_by_type[test_case_type] = {
                    "_id": embedded_id,
                    "content": combined_test_cases,
                }

                all_results.append(
                    {
                        "test_case_type": test_case_type,
                        "test_cases": combined_test_cases,
                    }
                )

                progress_message = (
                    f"{test_case_type} test cases generated for {base_stem}"
                )
                try:
                    collection.update_one(
                        {"_id": ObjectId(document_id)},
                        {
                            "$set": {
                                "test_cases": test_cases_by_type,
                                "status": 0,
                            },
                            "$push": {"progress": progress_message},
                        },
                    )
                except Exception as e:
                    print(
                        f"MongoDB update error (progress after {test_case_type}): {str(e)}"
                    )

                self.update_state(
                    state="PROGRESS",
                    meta={"status": "processing", "progress": progress_message},
                )

            try:
                collection.update_one(
                    {"_id": ObjectId(document_id)},
                    {"$set": {"status": 1, "progress": ["All test cases generated"]}},
                )
            except Exception as e:
                print("MongoDB update error (final):", str(e))

            result = {
                "file": base_stem,
                "model_used": model_name,
                "results": all_results,
                "document_id": document_id,
            }
            overall_results.append(result)

        final_result = {
            "message": "All documents processed and test cases generated.",
            "results": overall_results,
        }

        self.update_state(state="SUCCESS", meta=final_result)
        return final_result

    except Exception as e:
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise self.retry(exc=e)
