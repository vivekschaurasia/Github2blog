           +----------------------+
           |  User Input (GitHub  |
           |  Repo URL / Name)    |
           +----------+-----------+
                      |
                      v
           +----------------------+
           |  🧠 Agent 0: Orchestrator  |
           |  (Coordinates all agents) |
           +----------+-----------+
                      |
     +----------------+------------------------+
     |                                         |
     v                                         v
+------------------------+         +---------------------------+
| 🧠 Agent 1: Code Retriever |       | 🧠 Agent 2: Metadata Parser    |
| - Clone GitHub Repo      |       | - Extract repo info          |
| - Classify files (MCP)   |       |   (stars, forks, lang, etc.) |
| - Return file structure  |       +---------------------------+
+------------+-------------+
             |
             v
+------------------------------+
| 🧠 Agent 3: Component Summarizer |
| - Summarize key parts:         |
|   - README.md                  |
|   - src/ or notebooks/         |
|   - workflows/tests/configs    |
| - Output: Structured transcript|
+------------+------------------+
             |
             v
+-----------------------------+
| 🧠 Agent 4: Blog Generator   |
| - Convert transcript → blog |
| - Add code blocks, examples |
| - Format sections           |
+------------+----------------+
             |
             v
+-----------------------------+
| 🧠 Agent 5: Publisher Agent  |
| - Format as Markdown/HTML   |
| - Use Medium API to publish |
| - Add tags, SEO, title      |
+-----------------------------+

How is my Graph or workflow for this project?
