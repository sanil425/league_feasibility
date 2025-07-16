from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
from backend.solver import solve_scenario  # adjust if needed

app = FastAPI()

# Serve React frontend
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_build_path = os.path.join(current_dir, "../frontend/build")

app.mount("/", StaticFiles(directory=frontend_build_path, html=True), name="frontend")

# API route
@app.post("/simulate")
async def simulate(request: Request):
    data = await request.json()
    query = data.get("query", "")

    if not query:
        return JSONResponse({"error": "No query provided."}, status_code=400)

    result = solve_scenario(query)
    return JSONResponse(result)
