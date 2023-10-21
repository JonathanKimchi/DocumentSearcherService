import requests
from langchain.document_loaders import NotionDBLoader

NOTION_VERSION = "2022-06-28"
CONTENT_TYPE_JSON = "application/json"

NOTION_API_URL = "https://api.notion.com"
NOTION_SEARCH_URL = f"{NOTION_API_URL}/v1/search"

def get_notion_header(notion_api_key: str = "Test"):
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": CONTENT_TYPE_JSON,
        "Notion-Version": NOTION_VERSION,
    }
    return headers

def notion_get_blocks(page_id: str, headers: dict):
    res = requests.get(
        f"{NOTION_API_URL}/v1/blocks/{page_id}/children?page_size=100",
        headers=headers,
    )
    return res.json()

def notion_search(query: dict, headers: dict):
    res = requests.post(NOTION_SEARCH_URL, headers=headers, json=query)  # use json instead of data
    return res.json()

def get_page_text(page_id: str, headers: dict):
    page_text = []
    blocks = notion_get_blocks(page_id, headers)
    for item in blocks["results"]:
        item_type = item.get("type")
        content = item.get(item_type)
        if content.get("rich_text"):
            for text in content.get("rich_text"):
                plain_text = text.get("plain_text")
                page_text.append(plain_text)
    return page_text

def load_notion(headers: dict) -> list:
    documents = []
    all_notion_documents = notion_search({}, headers)
    items = all_notion_documents.get("results")
    for item in items:
        object_type = item.get("object")
        object_id = item.get("id")

        if object_type == "page":
            title_content = item.get("properties").get("title")
            title = ""
            if title_content:
                title = title_content.get("title")[0].get("text").get("content")
            elif item.get("properties").get("Name") and len(item.get("properties").get("Name").get("title")) > 0:
                title = item.get("properties").get("Name").get("title")[0].get("text").get("content")

            page_text = [title] + get_page_text(object_id, headers)
            text_per_page = ". ".join(page_text)
            if len(text_per_page) > 0:
                documents.append({'text': text_per_page})  # changed to a dictionary format for compatibility

    return documents

def convert_documents_into_text(messages):
    text = ''
    for message in messages:
        text += message['text']
        text += '\n\n'
    return text

# Integrate both functions
def fetch_and_convert_notion_data(notion_api_key: str = "Test"):
    headers = get_notion_header(notion_api_key)
    documents = load_notion(headers)
    text_data = convert_documents_into_text(documents)
    return text_data