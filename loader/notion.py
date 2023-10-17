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
    res = requests.post(NOTION_SEARCH_URL, headers=headers, data=query)
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

def get_notion_db_loader(database_id: str, headers: dict):
    # integration token == Bearer token
    print("headers:", headers)
    print("database_id:", database_id)
    return NotionDBLoader(
        integration_token=headers.get("Authorization").replace("Bearer ", ""),
        database_id=database_id.replace("-", ""),
        request_timeout_sec=30,
    )

def get_notion_loaders(headers: dict):
    document_loaders = []
    all_notion_documents = notion_search({}, headers)
    print(all_notion_documents)
    items = all_notion_documents.get("results")
    for item in items:
        object_type = item.get("object")
        object_id = item.get("id")
        url = item.get("url")
        title = ""
        
        if object_type == "database":
            document_loaders.append(get_notion_db_loader(object_id, headers))

    return document_loaders

def load_notion(headers: dict) -> list:
    documents = []
    all_notion_documents = notion_search({}, headers)
    print(all_notion_documents)
    items = all_notion_documents.get("results")
    for item in items:
        object_type = item.get("object")
        object_id = item.get("id")
        url = item.get("url")
        title = ""
        page_text = []

        if object_type == "page":
            title_content = item.get("properties").get("title")
            if title_content:
                title = (
                    title_content.get("title")[0].get("text").get("content")
                )
            elif item.get("properties").get("Name"):
                if len(item.get("properties").get("Name").get("title")) > 0:
                    title = (
                        item.get("properties")
                        .get("Name")
                        .get("title")[0]
                        .get("text")
                        .get("content")
                    )

            page_text.append([title])
            page_content = get_page_text(object_id, headers)
            page_text.append(page_content)

            flat_list = [item for sublist in page_text for item in sublist]
            text_per_page = ". ".join(flat_list)
            if len(text_per_page) > 0:
                documents.append(text_per_page)

    return documents

def convert_documents_into_text(messages):
        print("messages:", messages)
        text = ''
        for message in messages:
            # convert messages into text, including the user name and timestamp
            text += message['text']
            text += '\n\n'
            
        return text