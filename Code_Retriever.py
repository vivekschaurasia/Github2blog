import os
from github import Github


# Environment variables
GITHUB_TOKEN = os.getenv("API")
# Initialize clients
github_client = Github(GITHUB_TOKEN)




def code_retriever(url):
    repo_name = url.split("github.com/")[-1].rstrip("/")

    repo = github_client.get_repo(repo_name)

    contents = repo.get_contents("")
    file_structure = {}

    

    for content in contents:
        if content.type == "file":
            category = "source" if content.name.endswith((".py", ".js")) else \
                      "docs" if content.name.lower() == "readme.md" else \
                      "config" if content.name.endswith((".yaml", ".yml", ".json")) else "other"
            file_structure[content.name] = {
                "category": category,
                "content": content.decoded_content.decode("utf-8", errors="ignore")
            }



    content = file_structure
    print("Code Retrieval Done")
    return content

repo_url = "https://github.com/vivekschaurasia/Passive-Aggressive-Email-Rewriter"

content = code_retriever(repo_url)
#print(content)
