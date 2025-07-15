import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def call_gpt(prompt):
    system_prompt = """
You are an AI assistant that converts football season scenarios into structured JSON data.

Given a user prompt about football fixtures and outcomes, return:

- "target_team": the team the user is interested in.
- "target_rank": the final league position the user wants that team to achieve.
- "fixed_outcomes": list of specific matches and their results, formatted as:
    {
        "match": "Home Team vs Away Team",
        "result": "win/draw/loss from the perspective of target_team"
    }

If the user mentions "winning the league", assume target_rank = 1.
If the user mentions "avoiding relegation", assume target_rank = 17.
If the user mentions "top X", set target_rank to X.

Respond ONLY with pure JSON. Do not add any extra text.
"""
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    response_dict = response.model_dump()
    content = response_dict["choices"][0]["message"]["content"]

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print(f"Error parsing JSON: {content}")
        return None



def explain_solution(target_team, target_rank, full_solution, fixed_outcomes, feasible):
    """
    Calls GPT to explain the solution outcomes, highlighting key fixtures and user constraints.
    """

    intro = ""
    if feasible:
        intro += f"It is mathematically possible for {target_team} to finish in the top {target_rank}.\n"
    else:
        intro += f"It is NOT mathematically possible for {target_team} to finish in the top {target_rank}.\n"

    # Build the system prompt
    system_prompt = """
You are an expert sports analyst AI.

Given:
- The target team
- The desired final rank
- The full list of solved fixture outcomes
- The list of user-specified constraints (fixed match outcomes, e.g., "Manchester United loses to Arsenal")

Your task is to produce an analysis that explains:

1. Whether it is mathematically possible for the target team to reach the target rank.
2. How the user-specified constraints (the "fixed outcomes") impact the result. Explicitly mention them in your explanation.
    - For example: "Even though the team loses to Arsenal, there is still a feasible path because..."
3. List the games that the target team must win, draw, or lose (as per the solution).
4. Identify the OTHER key fixtures where rivals must lose or draw for the target team to succeed.
5. If the scenario is infeasible, explain exactly why. Is the target team too far behind? Are rivals uncatchable? Are there not enough matches left?
6. Highlight the **critical fixtures** that define the outcome (target team and other teams).
7. Keep the tone clear and analytical, like a sports pundit giving strategic playoff analysis.

Begin your response with:
- "It is possible because..." or 
- "It is not possible because..."

Use bullet points if helpful. Be concise but cover the logic fully.
"""

    # User prompt
    user_prompt = {
        "target_team": target_team,
        "target_rank": target_rank,
        "feasible": feasible,
        "all_fixture_outcomes": full_solution,
        "fixed_outcomes": fixed_outcomes
    }

    # Call OpenAI API
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_prompt)}
        ],
        temperature=0
    )

    # Parse response
    content = response.model_dump()["choices"][0]["message"]["content"]

    return intro + "\n" + content
