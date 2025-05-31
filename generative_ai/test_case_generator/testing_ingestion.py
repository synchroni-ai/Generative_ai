from data_ingestion.data_ingestion import fetch_document_text_from_s3_url

# Use a real S3 path to a test .txt, .pdf, or .docx file in your bucket
s3_url = "s3://gen.synchroni.xyz/dataspaces/683a9dc55f40b947ac2f5e53/documents/8b79cdb0-5f55-4b4f-96 3e-d3166f641cc5_design_documentation.pdf"

try:
    text = fetch_document_text_from_s3_url(s3_url)
    print("✅ Extracted Text:")
    print(text[:1000])  # print first 1000 chars
except Exception as e:
    print("❌ Error:", e)
