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



def explain_solution(target_team, target_rank, solution_outcomes, fixed_outcomes, feasible, probability, odds_data=None):
    """
    Generates a comprehensive explanation of the playoff/league scenario.

    Args:
        target_team (str): The team the user cares about.
        target_rank (int): The desired final league position.
        solution_outcomes (list): Required match results for feasibility.
        fixed_outcomes (list): User-specified fixed outcomes (forced results).
        feasible (bool): Whether the scenario is mathematically possible.
        probability (float): Monte Carlo estimated probability (real-world likelihood).
        odds_data (dict): Real-world odds for matches, used for deeper analysis.

    Returns:
        str: GPT-generated natural language explanation.
    """

    intro = ""
    if feasible:
        intro += f"✅ It is mathematically possible for {target_team} to finish in the top {target_rank}.\n"
    else:
        intro += f"❌ It is NOT mathematically possible for {target_team} to finish in the top {target_rank}.\n"

    # Build the system prompt for GPT
    system_prompt = """
You are an expert sports analyst AI.

Given:
- The user's favorite team and target rank.
- A list of required match outcomes for the target team to succeed.
- Any user-specified forced outcomes (fixed results).
- The estimated probability of this scenario happening (from Monte Carlo simulation).
- Real-world match odds (for each game) indicating how likely the required outcomes are.

Your job is to produce a detailed, narrative, and fan-friendly explanation.

If the scenario is impossible:
- Explain why (e.g., point gap too big, not enough matches left, etc.)
- Reference any user constraints that made it impossible.

If the scenario is possible:
- Clearly state that it is mathematically possible.
- Explain the realistic probability (e.g., "This scenario has a {probability}% chance of happening based on betting odds.")
- Interpret the probability in plain language (e.g., "This is a very unlikely scenario" or "This is possible but requires luck").
- In a free-flowing, paragraph-based style, describe the path required for the scenario to occur. For each required match result, briefly explain why it is important for the scenario (e.g., which teams need to drop points for the target team to rise). Add contextual comments for each result, especially for the most impactful or unlikely ones.
- Use bullet points for clarity, but avoid numbered lists or rigid sections. Group related ideas together naturally.
- Highlight the most critical and impactful games, and point out which results are considered upsets or very unlikely. Count and mention the number of upsets required for the scenario.
- Summarize the overall difficulty of the scenario and what makes it challenging.
- Always explicitly highlight and discuss the user-specified fixed outcomes (forced results), such as "Given Manchester United lose to Arsenal...". Comment on how these fixed results impact the scenario, whether they make the path harder, easier, or have a specific effect.
- For future visualisation, note that the required path could be represented as a tree structure if requested, but do not output a tree unless specifically asked.

Keep the tone clear, insightful, and engaging, like a TV analyst explaining playoff odds. Avoid using numbers for sections or steps.
"""

    # Prepare the user prompt as JSON
    user_prompt = {
        "target_team": target_team,
        "target_rank": target_rank,
        "feasible": feasible,
        "monte_carlo_probability": round(probability * 100, 4),  # As a %
        "required_outcomes": solution_outcomes,
        "fixed_outcomes": fixed_outcomes,
        "odds_data": odds_data if odds_data else "No odds data available"
    }

    # Call OpenAI API (official SDK, gpt-3.5-turbo-0125 or upgrade to gpt-4 if desired)
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_prompt)}
        ],
        temperature=0
    )

    # Extract GPT response text
    content = response.model_dump()["choices"][0]["message"]["content"]

    return intro + "\n" + content

