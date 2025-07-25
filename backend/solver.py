import pandas as pd
from pulp import LpProblem, LpMaximize, LpVariable, LpBinary, LpMinimize, LpConstraint, LpStatus, lpSum
from backend.gpt_interface import call_gpt, explain_solution
from backend.data_loader import load_data
from backend.monte_carlo import run_monte_carlo, get_cache_filename, save_sim, load_sim



# helpers




def match_team_name(input_name, team_list):
    for team in team_list:
        if input_name.lower() in team.lower():
            return team
    raise ValueError(f"Team name '{input_name}' not recognized in league.")


def load_prompt_from_file(prompt_header: str, prompts_file: str = "prompts.txt") -> str:
    """
    Loads a prompt from a file based on a header. Tries project root first, then backend/ directory.
    """
    import os
    search_paths = [prompts_file, os.path.join("backend", prompts_file)]
    for path in search_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            current_label = None
            prompt_lines = []
            for line in lines:
                if line.strip().startswith("###"):
                    found_label = line.strip()[3:].strip()
                    if current_label == prompt_header:
                        break
                    current_label = found_label
                    prompt_lines = []
                elif current_label == prompt_header:
                    prompt_lines.append(line.rstrip("\n"))
            if prompt_lines:
                return "\n".join(prompt_lines).strip()
        except FileNotFoundError:
            continue
    raise ValueError(f"Prompt with header '{prompt_header}' not found in {prompts_file} or backend/{prompts_file}.")


def solve_scenario(user_prompt: str) -> dict:
    # load (dummy) data
    standings_json, fixtures_json = load_data(dummy=True)

    # extract team info
    table = standings_json["standings"][0]["table"]

    # create list for standings
    standings_list = []
    for entry in table:
        standings_list.append({
            "team_id": entry["team"]["id"],
            "team_name": entry["team"]["name"],
            "points": entry["points"],
            "played": entry["playedGames"],
            "won": entry["won"],
            "drawn": entry["draw"],
            "lost": entry["lost"],
            "goal_difference": entry["goalDifference"],
            "goals_for": entry["goalsFor"],
            "goals_against": entry["goalsAgainst"],
            "position": entry["position"]
        })

    # convert list to dataframe
    standings_df = pd.DataFrame(standings_list)

    # extract fixture info
    fixtures = fixtures_json["matches"]

    # create list for fixtures
    fixtures_list = []
    for fixture in fixtures:
        fixtures_list.append({
            "match_id": fixture["id"],
            "matchday": fixture["matchday"],
            "home_team_id": fixture["homeTeam"]["id"],
            "home_team_name": fixture["homeTeam"]["name"],
            "away_team_id": fixture["awayTeam"]["id"],
            "away_team_name": fixture["awayTeam"]["name"],
            "utc_date": fixture["utcDate"],
            "status": fixture["status"]
        })

    # convert list to dataframe
    fixtures_df = pd.DataFrame(fixtures_list)

    # get simple fixture list for gpt
    gpt_fixture_list = []
    for idx, row in fixtures_df.iterrows():
        gpt_fixture_list.append(f"{row['home_team_name']} vs {row['away_team_name']}")

    # use user_prompt directly
    scenario = call_gpt(user_prompt)

    # extract scenario components safely, handling None scenario
    if scenario is None:
        return {"error": "Scenario could not be parsed from GPT. Please try again or check your input."}

    try:
        target_team_raw = scenario["target_team"]
        target_rank = scenario["target_rank"]
        fixed_outcomes = scenario["fixed_outcomes"]
    except (KeyError, TypeError):
        return {"error": "Scenario is missing required fields: 'target_team', 'target_rank', or 'fixed_outcomes'."}

    target_team = match_team_name(target_team_raw, standings_df["team_name"].tolist())

    # create optimization model
    model = LpProblem("Premier League Optimization", LpMinimize)

    # create variables for each match outcome
    home_win = {}
    draw = {}
    away_win = {}

    for idx, row in fixtures_df.iterrows():
        match_id = row["match_id"]
        home_win[match_id] = LpVariable(f"home_win_{match_id}", cat=LpBinary)
        draw[match_id] = LpVariable(f"draw_{match_id}", cat=LpBinary)
        away_win[match_id] = LpVariable(f"away_win_{match_id}", cat=LpBinary)

        # one outcome per match
        model += home_win[match_id] + draw[match_id] + away_win[match_id] == 1

    # apply fixed outcomes from gpt scenario
    for outcome in fixed_outcomes:
        match_desc = outcome["match"] # e.g Man United vs Arsenal
        result = outcome["result"] # e.g loss

        for idx, row in fixtures_df.iterrows():
            home = row["home_team_name"] 
            away = row["away_team_name"]
            match_id = row["match_id"]

            if match_desc == f"{home} vs {away}" or match_desc == f"{away} vs {home}":
                if result == "win":
                    if home == target_team:
                        model += home_win[match_id] == 1
                    elif away == target_team:
                        model += away_win[match_id] == 1
                elif result == "loss":
                    if home == target_team:
                        model += away_win[match_id] == 1
                    elif away == target_team:
                        model += home_win[match_id] == 1
                elif result == "draw":
                    model += draw[match_id] == 1

    # create current points dict
    team_points = standings_df.set_index("team_name")["points"].to_dict()

    # create future points dict (empty at start)
    future_points = {team: 0 for team in team_points.keys()}

    # sum up future points from match outcomes
    for idx, row in fixtures_df.iterrows():
        match_id = row["match_id"]
        home_team = row["home_team_name"]
        away_team = row["away_team_name"]

        future_points[home_team] += home_win[match_id] * 3 + draw[match_id]
        future_points[away_team] += away_win[match_id] * 3 + draw[match_id]

    # target team's total points
    target_final_points = team_points[target_team] + future_points[target_team]

    # rank constraint: must finish above (20 - target_rank) teams
    teams_to_beat = 20 - target_rank

    beat_vars = []
    big_M = 100

    for team in team_points:
        if team == target_team:
            continue  # skip self comparison

        # binary var: b = 1 if target_team beats team in points
        b = LpVariable(f"beat_{team}", cat=LpBinary)
        beat_vars.append(b)

        team_final_points = team_points[team] + future_points[team]

        # big-M constraint for ranking
        model += (target_final_points - team_final_points) >= 1 - big_M * (1 - b)

    # require at least (20 - target_rank) teams beaten
    model += lpSum(beat_vars) >= teams_to_beat

    # solve model (dummy objective, feasibility only)
    model += 0
    status = model.solve()

    # extract solution outcomes into list
    solution_outcomes = []
    for idx, row in fixtures_df.iterrows():
        match_id = row["match_id"]
        home = row["home_team_name"]
        away = row["away_team_name"]

        if home_win[match_id].varValue == 1:
            outcome = {"match": f"{home} vs {away}", "result": f"{home} wins"}
        elif away_win[match_id].varValue == 1:
            outcome = {"match": f"{home} vs {away}", "result": f"{away} wins"}
        elif draw[match_id].varValue == 1:
            outcome = {"match": f"{home} vs {away}", "result": "draw"}
        else:
            outcome = {"match": f"{home} vs {away}", "result": "unknown"}
        solution_outcomes.append(outcome)

    # Check feasibility using LP model
    if LpStatus[model.status] == "Optimal":
        feasible = True
        # Convert fixed_outcomes to Monte Carlo format (if needed)
        fixed_outcomes_mc = {}
        for outcome in fixed_outcomes:
            match = outcome["match"]
            result = outcome["result"]
            home, away = match.split(" vs ")
            if result == "win":
                if target_team == home:
                    fixed_outcomes_mc[match] = "home"
                else:
                    fixed_outcomes_mc[match] = "away"
            elif result == "loss":
                if target_team == home:
                    fixed_outcomes_mc[match] = "away"
                else:
                    fixed_outcomes_mc[match] = "home"
            elif result == "draw":
                fixed_outcomes_mc[match] = "draw"

        cache_filename = get_cache_filename(target_team, target_rank, fixed_outcomes_mc)
        cached_result = load_sim(cache_filename)
        if cached_result is not None:
            probability, odds_data = cached_result
        else:
            probability, odds_data = run_monte_carlo(target_team, target_rank, fixed_outcomes_mc, standings_df, fixtures_df)
            save_sim((probability, odds_data), cache_filename)
        explanation = explain_solution(
            target_team=target_team,
            target_rank=target_rank,
            solution_outcomes=solution_outcomes,
            fixed_outcomes=fixed_outcomes,
            feasible=True,
            probability=probability,
            odds_data=odds_data
        )
    else:
        feasible = False
        probability = 0.0
        odds_data = None
        explanation = explain_solution(
            target_team=target_team,
            target_rank=target_rank,
            solution_outcomes=solution_outcomes,
            fixed_outcomes=fixed_outcomes,
            feasible=False,
            probability=0.0,
            odds_data=None
        )
    return {
        "feasible": feasible,
        "probability": probability,
        "explanation": explanation,
        "target_team": target_team,
        "target_rank": target_rank,
        "solution_outcomes": solution_outcomes,
        "fixed_outcomes": fixed_outcomes,
        "odds_data": odds_data
    }

# Optional: keep CLI for testing
if __name__ == "__main__":
    # For testing, you can set a test prompt here
    test_prompt = "Can Manchester United finish in the top 10 even if they lose to Arsenal?"
    result = solve_scenario(test_prompt)
    if "error" in result:
        print(result["error"])
    else:
        print(result["explanation"])




