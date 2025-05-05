from fastapi import FastAPI, Query
from pydantic import BaseModel
from Github2blog import run_workflow

app = FastAPI()

class RepoRequest(BaseModel):
    repo_url: str

@app.post("/generate-blog/")
def generate_blog(data: RepoRequest):
    try:
        post_url = run_workflow(data.repo_url)
        return {"status": "success", "post_url": post_url}
    except Exception as e:
        return {"status": "error", "message": str(e)}


#uvicorn main_api:app --reload

