from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import os
from github import Github
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import requests

# Environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MEDIUM_TOKEN = os.getenv("MEDIUM_TOKEN")

# Initialize clients
github_client = Github(GITHUB_TOKEN)
llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)

# Define state schema
class WorkflowState(TypedDict):
    repo_url: str
    file_structure: dict
    metadata: dict
    transcript: str
    blog_content: str
    post_url: str

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
        template="Create a Medium blog post from this transcript:\n\n{transcript}\n\nMetadata:\n{metadata}\n\nInclude an intro, code snippets, examples, and conclusion. Format in Markdown."
    )
    
    metadata_summary = "\n".join([f"{k}: {v}" for k, v in metadata.items()])
    blog_content = llm.invoke(blog_prompt.format(transcript=transcript, metadata=metadata_summary)).content
    state["blog_content"] = blog_content
    return state

# Agent 5: Publisher Agent
def publisher_agent(state: WorkflowState) -> WorkflowState:
    blog_content = state["blog_content"]
    metadata = state["metadata"]
    
    headers = {
        "Authorization": f"Bearer {MEDIUM_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    user_response = requests.get("https://api.medium.com/v1/me", headers=headers)
    user_id = user_response.json()["data"]["id"]
    
    post_data = {
        "title": f"Exploring a {metadata['language']} Project on GitHub",
        "contentFormat": "markdown",
        "content": blog_content,
        "publishStatus": "public",
        "tags": [metadata["language"], "GitHub", "Programming"]
    }
    
    post_response = requests.post(
        f"https://api.medium.com/v1/users/{user_id}/posts",
        headers=headers,
        json=post_data
    )
    
    if post_response.status_code == 201:
        state["post_url"] = post_response.json()["data"]["url"]
    else:
        raise Exception(f"Failed to publish: {post_response.text}")
    
    return state

# Define the workflow graph
workflow = StateGraph(WorkflowState)

# Add nodes
workflow.add_node("orchestrator", orchestrator)
workflow.add_node("code_retriever", code_retriever)
workflow.add_node("metadata_parser", metadata_parser)
workflow.add_node("component_summarizer", component_summarizer)
workflow.add_node("blog_generator", blog_generator)
workflow.add_node("publisher", publisher_agent)

# Define edges
workflow.add_edge("orchestrator", "code_retriever")
workflow.add_edge("orchestrator", "metadata_parser")
workflow.add_edge("code_retriever", "component_summarizer")
workflow.add_edge("metadata_parser", "component_summarizer")
workflow.add_edge("component_summarizer", "blog_generator")
workflow.add_edge("blog_generator", "publisher")
workflow.add_edge("publisher", END)

# Set entry point
workflow.set_entry_point("orchestrator")

# Compile the graph
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
    return result["post_url"]

if __name__ == "__main__":
    repo_url = "https://github.com/user/sample-repo"
    post_url = run_workflow(repo_url)
    print(f"Blog published: {post_url}")


#From Krish Naik
# Below is how we can view the graph in a Jupyter Notebook
from IPython.display import Image, display
from langgraph import Graph
display(Image(graph.builder.get_graph().draw_mermaid_png()))