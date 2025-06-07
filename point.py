from fastapi import FastAPI
from fastapi.responses import JSONResponse
import asyncio

app = FastAPI()

@app.get("/")
def root():
    return {"message": "FastAPI is running"}

@app.get("/long-process")
async def long_process():
    # Simulate a long task (70 seconds)
    await asyncio.sleep(70)
    return JSONResponse(content={"status": "done", "duration_seconds": 70})
