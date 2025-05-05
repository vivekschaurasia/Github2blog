from langgraph.graph import StateGraph, END # type: ignore
from typing import TypedDict, Annotated
import os
from github import Github # type: ignore
from langchain_openai import ChatOpenAI # type: ignore
from langchain_core.prompts import PromptTemplate # type: ignore
import requests # type: ignore

from dotenv import load_dotenv # type: ignore

load_dotenv(override=True)


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
dev_api = os.getenv("DEV_API")
#MEDIUM_TOKEN = os.getenv("MEDIUM_TOKEN")
llm = ChatOpenAI(model="gpt-4-turbo", api_key=OPENAI_API_KEY)


# Initialize clients
github_client = Github(GITHUB_TOKEN)


# Define reducers for concurrent access
def merge_strings(existing, new):
    """Reducer for repo_url: ensure only one value."""
    if existing and new and existing != new:
        raise ValueError(f"Conflicting repo_url values: {existing} vs {new}")
    return new or existing

def merge_dict(existing, new):
    """Reducer for file_structure: return the new dict (only one node updates)."""
    return new or existing




"""
This class is not used like a normal Python class — it’s used to tell Python:

"Hey, I’m expecting a dictionary that must have these keys, and their values must be of these types."
"""
#Defining the state schema
class WorkflowState(TypedDict):

    repo_url: Annotated[str, merge_strings]  # Allow concurrent access
    #repo_url: str
    #file_structure: dict
    file_structure: Annotated[dict, merge_dict]
    metadata: Annotated[dict, merge_dict]
    #metadata: dict
    #transcript: str
    transcript: Annotated[str, merge_strings]
    #blog_content: str
    blog_content: Annotated[str, merge_strings]
    #post_url: str
    post_url: Annotated[str, merge_strings]


# Agent 0: Orchestrator (simply passes input to next agents)
def orchestrator(state: WorkflowState) -> WorkflowState:
    print("Orchestrating workflow...")
    return state

# Agent 1: Code Retriever
def code_retriever(state: WorkflowState) -> WorkflowState:
    repo_name = state["repo_url"].split("github.com/")[-1].rstrip("/")
    repo = github_client.get_repo(repo_name)
    contents = repo.get_contents("")
    file_structure = {}
    
    # Simple file classification (extend with MCP logic)
    for content in contents:
        if content.type == "file":
            category = "source" if content.name.endswith((".py", ".js")) else \
                      "docs" if content.name.lower() == "readme.md" else \
                      "config" if content.name.endswith((".yaml", ".yml", ".json")) else "other"
            file_structure[content.name] = {
                "category": category,
                "content": content.decoded_content.decode("utf-8", errors="ignore")
            }
    
    state["file_structure"] = file_structure
    return state
"""
import logging

# Agent 1: Code Retriever
def code_retriever(state: WorkflowState) -> WorkflowState:
    try:
        repo_name = state["repo_url"].split("github.com/")[-1].rstrip("/")
        repo = github_client.get_repo(repo_name)
        contents = repo.get_contents("")
        file_structure = {}
        
        for content in contents:
            if content.type == "file":
                category = "source" if content.name.endswith((".py", ".js")) else \
                          "docs" if content.name.lower() == "readme.md" else \
                          "config" if content.name.endswith((".yaml", ".yml", ".json")) else "other"
                
                # Check if content is decodable
                if content.decoded_content is None:
                    logging.warning(f"Skipping file {content.name}: No decodable content (possibly binary)")
                    file_structure[content.name] = {
                        "category": category,
                        "content": "[Non-decodable content]"
                    }
                else:
                    try:
                        file_content = content.decoded_content.decode("utf-8", errors="ignore")
                        file_structure[content.name] = {
                            "category": category,
                            "content": file_content
                        }
                    except Exception as e:
                        logging.warning(f"Failed to decode file {content.name}: {str(e)}")
                        file_structure[content.name] = {
                            "category": category,
                            "content": f"[Error decoding content: {str(e)}]"
                        }
        
        state["file_structure"] = file_structure
    except Exception as e:
        logging.error(f"Error in code_retriever: {str(e)}")
        state["file_structure"] = {"error": str(e)}
    return state
"""

# Agent 2: Metadata Parser
def metadata_parser(state: WorkflowState) -> WorkflowState:
    repo_name = state["repo_url"].split("github.com/")[-1].rstrip("/")
    repo = github_client.get_repo(repo_name)
    metadata = {
        "stars": repo.stargazers_count,
        "forks": repo.forks_count,
        "language": repo.language,
        "description": repo.description or "No description",
        "last_updated": repo.updated_at
    }
    
    state["metadata"] = metadata
    return state

# Agent 3: Component Summarizer
def component_summarizer(state: WorkflowState) -> WorkflowState:
    file_structure = state["file_structure"]
    metadata = state["metadata"]
    
    transcript_prompt = PromptTemplate(
        input_variables=["files", "metadata"],
        template="Summarize the key components of this GitHub repo:\n\nFiles:\n{files}\n\nMetadata:\n{metadata}\n\nOutput a structured transcript covering README, source code, and configs/workflows."
    )
    
    files_summary = "\n".join([f"{name} ({data['category']}):\n{data['content'][:500]}..." for name, data in file_structure.items()])
    metadata_summary = "\n".join([f"{k}: {v}" for k, v in metadata.items()])
    transcript = llm.invoke(transcript_prompt.format(files=files_summary, metadata=metadata_summary)).content
    
    state["transcript"] = transcript
    return state

# Agent 4: Blog Generator
def blog_generator(state: WorkflowState) -> WorkflowState:
    transcript = state["transcript"]
    metadata = state["metadata"]
    
    blog_prompt = PromptTemplate(
        input_variables=["transcript", "metadata"],
        #template="Create a Medium blog post from this transcript:\n\n{transcript}\n\nMetadata:\n{metadata}\n\n The blog should be a detailed blog. The blog should be accurate technically and as in depth as possible. \n\nInclude an intro, as much as code snippets as possible and explanation of those code snippets, examples, and conclusion. Format in Markdown."
        template="""
You are a technical writer specialized in explaining GitHub repositories in a clear, engaging, and structured blog format.

Given the following GitHub repository summary and file analysis, generate a detailed and well-formatted blog post in Markdown format suitable for publishing on Medium or Dev.to.

--- 
🎯 Objective: Explain what the repository does, how it works, its key components, and how to use it.

🧑‍💻 Target Audience: Developers who may want to use, learn from, or contribute to the project. Assume they understand basic programming but not this specific repo.

✍️ Blog Format:
1. **Title** (Catchy but clear)
2. **Introduction** (Purpose and what problem it solves)
3. **How it Works** (Explain the architecture, key features, and components)
4. **Code Walkthrough** (Summarize important files like main.py, utils.py, etc.)
5. **How to Use It** (Setup, install, run, with example commands)
6. **Real-World Applications** (Where this can be useful)
7. **Conclusion** (Wrap-up and future ideas)
8. **Call to Action** (Fork it, try it, contribute, etc.)

Use bullet points and code snippets where helpful. Make it sound slightly conversational and enthusiastic, like a developer blogging about a cool project they made on a weekend.

---
📦 GitHub Repo Summary:
{transcript}

📌 Metadata:
{metadata}
"""
    )
    
    metadata_summary = "\n".join([f"{k}: {v}" for k, v in metadata.items()])
    blog_content = llm.invoke(blog_prompt.format(transcript=transcript, metadata=metadata_summary)).content
    state["blog_content"] = blog_content
    return state


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


def publisher_agent(state: WorkflowState) -> WorkflowState:
    """
    Publishes a blog post to Dev.to using the official API.
    """

    headers = {
        "api-key": dev_api,
        "Content-Type": "application/json"
    }
    raw_tags = state["metadata"].get("tags", [state["metadata"]["language"], "GitHub", "Programming"])
    
    #tags = sanitize_tags(raw_tags)
    tags = 'github', 'programming'
    print(f"Tags are bellow. Only 2: {tags}")
    # Create the payload
    blog_content = state["blog_content"]
    metadata = state["metadata"]
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




#Defining the workflow graph
workflow = StateGraph(WorkflowState)

#Adding nodes to the graph
workflow.add_node("Orchestrator", orchestrator)
workflow.add_node("code_retriever", code_retriever)
workflow.add_node("metadata_parser", metadata_parser)
workflow.add_node("component_summarizer", component_summarizer)
workflow.add_node("blog_generator", blog_generator)
workflow.add_node("publisher", publisher_agent)

#Adding edges to the graph
workflow.add_edge("Orchestrator", "code_retriever")
workflow.add_edge("Orchestrator", "metadata_parser")
workflow.add_edge("code_retriever", "component_summarizer")
workflow.add_edge("metadata_parser", "component_summarizer")
workflow.add_edge("component_summarizer", "blog_generator")
workflow.add_edge("blog_generator", "publisher")
workflow.add_edge("publisher", END)

#Setting the entry point of the graph
workflow.set_entry_point("Orchestrator")


app = workflow.compile()



# Run the workflow
def run_workflow(repo_url: str):
    initial_state = {
        "repo_url": repo_url,
        "file_structure": {},
        "metadata": {},
        "transcript": "",
        "blog_content": "",
        "post_url": ""
    }
    result = app.invoke(initial_state)
    print(result)
    print(" /n"* 8)
   
    print(result["post_url"])
    return result["post_url"]

if __name__ == "__main__":

    repo_url = "https://github.com/vivekschaurasia/Passive-Aggressive-Email-Rewriter"
    repo_url = "https://github.com/vivekschaurasia/Capstone-Project"
    repo_url = "https://github.com/vivekschaurasia/Github2blog"
    repo_url = "https://github.com/AbhinavKalsi/Capstone_IDAI780"
    
    post_url = run_workflow(repo_url)
    print(f"Blog published: {post_url}")