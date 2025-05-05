import requests
from Blog_generator import blog_generator
from Metadata_Parser import metadata_parser
from Code_Retriever import code_retriever
from Component_summarizer import component_summarizer
import os



import re

def sanitize_tags(tags):
    clean_tags = []
    for tag in tags:
        # Convert to lowercase, remove non-alphanumeric, and replace spaces with dashes
        tag = tag.lower()
        tag = re.sub(r"[^a-z0-9 ]", "", tag)
        tag = tag.replace(" ", "-")
        clean_tags.append(tag)
    return clean_tags[:5]  # Dev.to allows max 5 tags


def publisher_agent(metadata: dict, blog_content: str) -> dict:
    """
    Publishes a blog post to Dev.to using the official API.
    """

    headers = {
        "api-key": "qYEtKhaNu6DvCEVjUTaAHi8X",
        "Content-Type": "application/json"
    }
    
    raw_tags = metadata.get("tags", [metadata["language"], "GitHub", "Programming"])
    #tags = sanitize_tags(raw_tags)
    tags = 'github', 'programming'
    print(f"Tags are bellow. Only 2: {tags}")
    # Create the payload
    post_data = {
        "article": {
            "title": f"Exploring a {metadata['language']} Project on GitHub",
            "published": True,
            "body_markdown": blog_content,
            "tags": tags,
            "canonical_url": metadata.get("repo_url", ""),  # Optional
            "series": "GitHub Auto Blog Series"
        }
    }
    

    # Make the request
    response = requests.post("https://dev.to/api/articles", headers=headers, json=post_data)

    # Handle response
    if response.status_code == 201:
        blog_url = response.json()["url"]
        print(f"✅ Blog published successfully: {blog_url}")
        return {"post_url": blog_url}
    else:
        print(f"❌ Failed to publish: {response.status_code}")
        print(response.text)
        return {"error": response.text}


repo_url = "https://github.com/vivekschaurasia/Passive-Aggressive-Email-Rewriter"
x = metadata_parser(repo_url)
y = code_retriever(repo_url)

publisher_agent(metadata_parser(repo_url) , blog_generator(component_summarizer(x , y) , x))

