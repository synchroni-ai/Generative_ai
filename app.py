import streamlit as st
import requests
import json

# --- API Base URL ---
API_BASE_URL = "http://localhost:8000"  # Adjust if your API is running elsewhere


def process_pdf(pdf_file):
    """Uploads the PDF to the API and returns the cleaned text."""
    files = {"file": pdf_file}
    try:
        response = requests.post(f"{API_BASE_URL}/process_pdf/", files=files)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        return data.get("cleaned_text")
    except requests.exceptions.RequestException as e:
        st.error(f"Error processing PDF: {e}")
        return None


def generate_test_cases(
    cleaned_text, prompt_file_path=None, chunk_size=None, cache_key=None
):
    """Calls the API to generate test cases."""
    params = {"cleaned_text": cleaned_text}
    if prompt_file_path:
        params["prompt_file_path"] = prompt_file_path
    if chunk_size:
        params["chunk_size"] = chunk_size
    if cache_key:
        params["cache_key"] = cache_key

    try:
        response = requests.get(f"{API_BASE_URL}/generate_test_cases/", params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Error generating test cases: {e}")
        return None


# --- Streamlit UI ---
st.title("BRD Test Case Generator")

# 1. PDF Upload
st.header("1. Upload BRD PDF")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    with st.spinner("Processing PDF..."):
        cleaned_text = process_pdf(uploaded_file)

    if cleaned_text:
        st.success("PDF processed successfully!")

        # 2. Configuration
        st.header("2. Configuration (Optional)")
        prompt_file_path = st.text_input("Prompt File Path (optional)")
        chunk_size = st.number_input(
            "Chunk Size (optional)",
            min_value=100,
            max_value=10000,
            value=4000,
            step=100,
        )
        use_cache = st.checkbox("Use Cache", value=False)
        cache_key = (
            st.session_state.get("cache_key", None) if use_cache else None
        )  # get cache_key from session state if cache is selected

        if use_cache and cache_key:
            st.write(f"Using cached test cases with key: {cache_key}")
        elif use_cache:
            st.write("Generating new test cases - first run")
        # 3. Generate Test Cases
        st.header("3. Generate Test Cases")
        if st.button("Generate Test Cases"):
            with st.spinner("Generating test cases..."):
                result = generate_test_cases(
                    cleaned_text, prompt_file_path, chunk_size, cache_key
                )

            if result:
                st.success("Test cases generated successfully!")
                st.session_state["test_cases"] = result.get("test_cases")
                st.session_state["cache_key"] = result.get("cache_key")
                st.write("Test Cases:")
                st.code(st.session_state.get("test_cases", ""), language="text")
                st.write(f"Cache Key: {st.session_state.get('cache_key', 'N/A')}")
            else:
                st.error("Failed to generate test cases.")

        # 4. Display Generated Test Cases
        st.header("4. Test Cases")
        if "test_cases" in st.session_state and st.session_state["test_cases"]:
            st.write("Test Cases:")
            st.code(st.session_state["test_cases"], language="text")
        else:
            st.info("Generate test cases to see the results.")
    else:
        st.error("Failed to process the PDF. Please check the file.")
else:
    st.info("Upload a PDF file to begin.")
