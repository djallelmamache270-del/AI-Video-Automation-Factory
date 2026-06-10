from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import sqlite3, uuid, json

app = FastAPI(title="AI Video Factory API")
DB_PATH = '/home/djallel/ai_video_factory/factory.db'

class ScriptLine(BaseModel):
    speaker: str
    text: str

class JobCreate(BaseModel):
    title: str
    script: List[ScriptLine]

@app.on_event("startup")
def startup():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY, 
            title TEXT, 
            script_text TEXT, 
            status TEXT DEFAULT "pending"
        )
    ''')
    conn.close()

@app.post("/api/v1/videos/create-job", status_code=202)
def create_job(job: JobCreate):
    try:
        job_id = str(uuid.uuid4())
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO jobs VALUES (?, ?, ?, 'pending')", 
                     (job_id, job.title, json.dumps([line.dict() for line in job.script])))
        conn.commit()
        conn.close()
        return {"status": "accepted", "job_id": job_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
