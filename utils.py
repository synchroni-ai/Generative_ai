# Import dependencies
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.vector_stores.azureaisearch import AzureAISearchVectorStore
from llama_index.core.postprocessor import SentenceTransformerRerank
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from llama_index.vector_stores.azureaisearch import (
    IndexManagement,
    MetadataIndexFieldType,
)
from llama_index.core import StorageContext
from dotenv import load_dotenv
import os
import requests
import tempfile
import json

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Azure OpenAI setup
Settings.llm = AzureOpenAI(
    model="gpt-4o",
    deployment_name="document-tagging-model",
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version="2024-12-01-preview",
    temperature=0.7,
    max_tokens=8192,
    context_window=200000,
)

Settings.embed_model = AzureOpenAIEmbedding(
    model="text-embedding-3-large",
    deployment_name="text-embedding-3-large",
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version="2024-12-01-preview",
)

# Azure AI Search setup
search_client = SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name="doc-tagging-taxonomy-index-new",
    credential=AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"]),
)

index_client = SearchIndexClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"]),
)

metadata_fields = {
    "author": "author",
    "theme": ("topic", MetadataIndexFieldType.STRING),
    "director": "director",
}

vector_store = AzureAISearchVectorStore(
    search_or_index_client=search_client,
    filterable_metadata_field_keys=metadata_fields,
    index_management=IndexManagement.VALIDATE_INDEX,
    id_field_key="id",
    chunk_field_key="chunk",
    embedding_field_key="embedding",
    embedding_dimensionality=1536,
    metadata_string_field_key="metadata",
    doc_id_field_key="doc_id",
)

storage_context = StorageContext.from_defaults(vector_store=vector_store)
rerank = SentenceTransformerRerank(
    model="cross-encoder/ms-marco-MiniLM-L2-v2", top_n=10
)


def download_document(document_url):
    response = requests.get(document_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download document: {response.status_code}")

    file_extension = os.path.splitext(document_url)[1].lower()

    if not file_extension:
        content_type = response.headers.get("content-type", "").lower()
        if "pdf" in content_type:
            file_extension = ".pdf"
        elif "html" in content_type or "htm" in content_type:
            file_extension = ".html"
        elif "msword" in content_type or "doc" in content_type:
            file_extension = ".doc"
        elif "docx" in content_type:
            file_extension = ".docx"
        else:
            file_extension = ".txt"

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
    temp_file.write(response.content)
    temp_file.close()
    return temp_file.name


def clean_json_text(text):
    text = text.replace("```json", "").replace("```", "")
    start = text.find("{")
    end = text.rfind("}") + 1
    return text[start:end].strip() if start != -1 and end != 0 else None


def process_document(document_path, existing_tag):
    document_analysis1 = SimpleDirectoryReader(input_files=[document_path]).load_data()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index1 = VectorStoreIndex.from_documents(document_analysis1)
    index2 = VectorStoreIndex.from_documents([], storage_context=storage_context)

    query_engine1 = index1.as_query_engine(
        node_postprocessors=[rerank], similarity_top_k=10
    )
    query_engine2 = index2.as_query_engine(
        node_postprocessors=[rerank], similarity_top_k=10
    )

    get_description_of_document = query_engine1.query(
        """You are an expert document analyst. Analyze the pdf document thoroughly and provide a high level understanding in the following structured format:
note: Do not use synonyms, just use the exact words from the document.
1. DOCUMENT OVERVIEW:
   - What is the main purpose of this document?
   - Who is the intended audience?

2. KEY CONTENT ANALYSIS:
   - What are the main topics covered?
   - What are the key decisions, policies, or procedures being discussed?
   - What are the primary objectives or outcomes described?

3. CONTEXT AND RELATIONSHIPS:
   - How does this document relate to organizational processes?
   - What business functions or activities does it impact?
   - What are the key organizational areas involved?

4. CORE CONCEPTS:
   - List the 5-7 most important concepts or themes
   - Identify any specific technical or domain-specific terminology
   - Note any recurring themes or patterns

5. SUMMARY:
   Provide a 4-5 sentence comprehensive summary that captures:
   - The document's essential purpose
   - Its main subject matter
   - Key implications or impacts
   - Primary organizational context
6. Suggested tags:
    - Give 5-10 tags that are relevant to the document.
write document name in the response. Format your response in clear, concise bullet points under each section.
"""
    )

    response = query_engine2.query(
        f"""You are a document classification assistant. Given the content of the document below, analyze it and suggest the most relevant high-level tag that categorizes the document. 
The tag should reflect the **primary administrative domain or purpose** of the content.
Use the exact authorized terms in Taxonomy_terms_notdepricated_taggable_with_other_labels.xlsx. 
Where column name ID, Term_name, OtherLabels, Term_Description are Id of ther term, name of the term, other labels of the term, description of the term respectively.

Instructions:
1. Thoroughly analyze the document's content, including subject matter, context, and key concepts to understand the **main function** of the document.

2. Here is the structured description of the document: {get_description_of_document}. \n
3. Select the most relevant tags from Taxonomy_terms_notdepricated_taggable.xlsx that best represent the **core function**, as described above. 
   - To find the most relevant tags, always use the column OtherLabels and OtherLabels in Taxonomy_terms_notdepricated_taggable_with_other_labels.xlsx.
   - Do not ignore a term if it is high level or does not encompass the nuanace of the document, read the OtherLabels and OtherLabels and then suggest the term(remember the terms actual meaning is explained in Term_Description and OtherLabels, so to suggest the term utilise the Term_Description and OtherLabels to suggest the term)
   - Prioritize terms that capture the documents primary procedural or operational intent.
   - Do not overemphasize secondary compliance or environmental mentions unless they are the primary focus.
   - To suggest new tags, use the column OtherLabels and Term_Description in Taxonomy_terms_notdepricated_taggable_with_other_labels.xlsx and suggest term associated with the OtherLabels and Term_Description.
4. Match tags **exactly** as written in the taxonomy (case-sensitive).
5. Identify any **missing but important concepts** that could be added to the taxonomy, if applicable.
6. Ensure suggested tags are specific, meaningful, and relevant to the document.
<scratchpad> Use this space to brainstorm and reason about the document and sugget tags by understanding OtherLabels and Term_Description </scratchpad>

Document name: [filename]
Suggested tags: [terms only from Taxonomy_terms_notdepricated_taggable_with_other_labels.xlsx not more than 3. eg Term1, Term2, Term3. Do not suggest new terms which are not in the provided Term_name]
Tag_Id: [ID of suggested tags from Taxonomy_terms_notdepricated_taggable_with_other_labels.xlsx. Always find the associated ID for the suggested tag]
likelyness: [in the range of 0-10 how much the term is relevant to the document eg. Term1: 10, Term2: 8, Term3: 6 ]
reason: [reason for term1, reason for term2, reason for term3]   
New suggested tags: [2-3 most important missing terms, comma-separated(if any). They should NOT be in the provided Term_name, always give synonyms]

Return ONLY in this exact JSON format with no additional text:
{{
  "Document name": "[filename]",
  "Suggested tags": ["Term1", "Term2", "Term3"],
  "Tag_Id": ["Term1", "TermID2", "TermID3"],
  "likelyness": {{
    "Term1": 10,
    "Term2": 8,
    "Term3": 6
  }},
  "reason": {{
    "Term1": "reason for term1",
    "Term2": "reason for term2",
    "Term3": "reason for term3"
  }},
  "New suggested tags": ["missing_term1", "missing_term2"]
}}"""
    )

    find_reason = query_engine1.query(
        f"""Here is your suggested tag for given document. 
{response}
Here is the existing tag that was tagged by Human. existing tag: {existing_tag}
Write a resson why you did or did not suggest the same tag in the reponse.
Return only in the following json format:
{{
  "Reason": "reason"
}}"""
    )

    json_text = clean_json_text(str(response))
    reason_text = clean_json_text(str(find_reason))
    tag_json = json.loads(json_text)
    reason_json = json.loads(reason_text)

    return {
        "Document": os.path.basename(document_path),
        "Existing_tag": existing_tag,
        "Suggested_Tag_LLM": tag_json.get("Suggested tags", []),
        "Suggested_Tag's_Unique_ID": tag_json.get("Tag_Id", []),
        "LLM's Reasoning": tag_json.get("reason", {}),
        "Likeliness(1-10)": tag_json.get("likelyness", {}),
        "Additional_Keywords_LLM": tag_json.get("New suggested tags", []),
        "Reason_for_Tag_Match_Mismatch": reason_json.get("Reason", ""),
    }
