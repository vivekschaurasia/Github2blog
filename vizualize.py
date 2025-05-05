# Compile the graph
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import os
from IPython.display import Image, display

import requests
from Github2blog import workflow


app = workflow.compile()

print(app.get_graph().draw_mermaid())

from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles


# Save the PNG to a file
output_path = "workflow_graph.png"
with open(output_path, "wb") as f:
    f.write(app.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API))
print(f"Graph saved as {output_path}")

# Optionally open the file (Windows-specific)

os.startfile(output_path)


