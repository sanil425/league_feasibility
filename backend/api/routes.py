from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.solver import solve_scenario
from pydantic import BaseModel

app = FastAPI()

# Enable CORS for all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to ["http://localhost:3000"] for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScenarioRequest(BaseModel):
    user_prompt: str

@app.post("/simulate/")
def simulate_league(request: ScenarioRequest):
    result = solve_scenario(request.user_prompt)
    return result