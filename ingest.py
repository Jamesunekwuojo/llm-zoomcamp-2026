# For reusability sake.. the original code in the notebook will be divided into smaller files: ingest and reg-helper for now..

import requests
from minsearch import Index

def load_faq_data():
    docs_url = "https://datatalks.club/faq/json/courses.json"
    response = requests.get(docs_url)
    courses_raw = response.json()

    documents = []
    url_prefix = "https://datatalks.club/faq"

    for course in courses_raw:
        course_url = f"""{url_prefix}{course["path"]}"""
        course_response = requests.get(course_url)
        course_response.raise_for_status()
        course_data = course_response.json()

        documents.extend(course_data)

    return documents

def build_index(documents):
    index = Index(
        text_fields=["question", "section", "answer"],
        keyword_fields=["course"]
    )
    index.fit(documents)
    return index





# # PERSONAL RESEARCH

# An index is a data structure used to speed up the retrieval of information. It works exactly like the index at the back of a textbook: instead of reading every page to find a topic, you look up the topic in the index to find the exact page number


# A persistent search index typically refers to a search index that is stored on a non-volatile medium (like a hard drive or SSD) rather than strictly in volatile memory (RAM). This ensures that your indexed data is preserved even if the system reboots or loses power, making retrieval both durable and efficient