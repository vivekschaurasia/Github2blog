from Code_Retriever import code_retriever # type: ignore
from Metadata_Parser import metadata_parser
import os
from github import Github
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

llm = ChatOpenAI(model="gpt-3.5-turbo", api_key="API")

# Agent 3: Component Summarizer
def component_summarizer(metadata , file_structure):
    file_structure = file_structure
    metadata = metadata
    
    transcript_prompt = PromptTemplate(
        input_variables=["files", "metadata"],
        template="Summarize the key components of this GitHub repo:\n\nFiles:\n{files}\n\nMetadata:\n{metadata}\n\nOutput a structured transcript covering README, source code, and configs/workflows."
    )
    
    files_summary = "\n".join([f"{name} ({data['category']}):\n{data['content'][:500]}..." for name, data in file_structure.items()])
    metadata_summary = "\n".join([f"{k}: {v}" for k, v in metadata.items()])
    transcript = llm.invoke(transcript_prompt.format(files=files_summary, metadata=metadata_summary)).content
    
    return transcript


repo_url = "https://github.com/vivekschaurasia/Passive-Aggressive-Email-Rewriter"

transcript = component_summarizer(metadata_parser(repo_url) , code_retriever(repo_url))

print(transcript)
