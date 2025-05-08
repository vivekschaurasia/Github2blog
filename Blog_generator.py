from Code_Retriever import code_retriever # type: ignore
from Metadata_Parser import metadata_parser
from Component_summarizer import component_summarizer
import os
from github import Github # type: ignore
from langchain_openai import ChatOpenAI # type: ignore
from langchain_core.prompts import PromptTemplate # type: ignore



llm = ChatOpenAI(model="gpt-3.5-turbo", api_key="API")


# Agent 4: Blog Generator
def blog_generator(transcript , metadata ):
    transcript = transcript
    metadata = metadata
    
    blog_prompt = PromptTemplate(
        input_variables=["transcript", "metadata"],
        template="Create a Medium blog post from this transcript:\n\n{transcript}\n\nMetadata:\n{metadata}\n\nInclude an intro, code snippets, examples, and conclusion. Format in Markdown."
    )
    
    metadata_summary = "\n".join([f"{k}: {v}" for k, v in metadata.items()])
    blog_content = llm.invoke(blog_prompt.format(transcript=transcript, metadata=metadata_summary)).content
    return blog_content



repo_url = "https://github.com/vivekschaurasia/Passive-Aggressive-Email-Rewriter"


x = metadata_parser(repo_url)
y = code_retriever(repo_url)
blog = blog_generator(component_summarizer(x , y) , x)

print("Blog Generation Starts: /n/n")
print(blog)
