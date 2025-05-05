import os
from github import Github


# Environment variables
GITHUB_TOKEN = os.getenv("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")
# Initialize clients
github_client = Github(GITHUB_TOKEN)


def metadata_parser(url):
    repo_name = url.split("github.com/")[-1].rstrip("/")
    repo = github_client.get_repo(repo_name)

    metadata = {
        "stars": repo.stargazers_count,
        "forks": repo.forks_count,
        "language": repo.language,
        "description": repo.description or "No description",
        "last_updated": repo.updated_at
    }
    
    print("Metadata Done")
    return metadata



repo_url = "https://github.com/vivekschaurasia/Passive-Aggressive-Email-Rewriter"

#print(metadata_parser(repo_url))