from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

from backend.api.solver import solve_scenario

app = FastAPI()

# Serve React frontend (Render compatible)
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_build_path = os.path.join(current_dir, "../../frontend/build")

if os.path.exists(frontend_build_path):
    app.mount("/", StaticFiles(directory=frontend_build_path, html=True), name="frontend")


# Pydantic model for input
class ScenarioRequest(BaseModel):
    query: str


# API route
@app.post("/simulate/")
async def simulate(request: ScenarioRequest):
    # Use the user query directly with your solver
    result = solve_scenario(request.query)
    
    # Return the entire solver result as JSON
    return JSONResponse(result)
