import random
from get_odds import get_odds
import pickle
import os
import json
import hashlib

# set number of simulations
NUM_SIMULATIONS = 10000


def simulate_remaining_season(odds_data, base_table, fixtures, user_goal_check, fixed_outcomes):
    """
    Simulates one version of the remaining season using match odds and user constraints.

    Args:
        odds_data (dict): Probabilities for each match from get_odds()
        base_table (dict): Current league standings (team points etc.)
        fixtures (list): Remaining matches as tuples (home, away)
        user_goal_check (function): Function to check if the user goal is met
        fixed_outcomes (dict): User-specified fixed match outcomes, e.g., {"Arsenal vs Man City": "home"}

    Returns:
        bool: True if the user goal is met in this simulation, False otherwise
    """

    simulated_results = {}

    # simulate all remaining fixtures
    for fixture in fixtures:
        home, away = fixture
        match_key = f"{home} vs {away}"

        # get probabilities from odds data
        if match_key in odds_data:
            probs = odds_data[match_key]["probabilities"]
        else:
            # if no odds, fallback to equal probabilities (1/3 each outcome)
            probs = {'home': 1/3, 'draw': 1/3, 'away': 1/3}

        # randomly pick the match result based on probabilities
        outcome = random.choices(['home', 'draw', 'away'], weights=[probs['home'], probs['draw'], probs['away']])[0]

        # store the simulated outcome
        simulated_results[match_key] = outcome

    # apply simulation results and fixed outcomes to the table
    final_table = apply_simulation(base_table, simulated_results, fixed_outcomes)

    # check if user goal is met in this simulated season
    return user_goal_check(final_table)


def make_user_goal_check(target_team, target_rank):
    """
    Creates a user goal check function dynamically, so it's flexible for any team and rank.

    Args:
        target_team (str): Team the user wants to track, e.g., "Arsenal"
        target_rank (int): Desired rank, e.g., 4 for top 4

    Returns:
        function: A function that takes final_table and returns True/False
    """

    def user_goal_check(final_table):
        # get team position from final_table, check if it's at or better than target_rank
        pos = final_table.get(target_team, {}).get('position')
        return pos is not None and pos <= target_rank

    return user_goal_check


def run_monte_carlo(target_team, target_rank, fixed_outcomes, standings_df, fixtures_df, num_simulations=NUM_SIMULATIONS):
    """
    Runs full Monte Carlo simulation loop to estimate probability of user-defined scenario.

    Args:
        target_team (str): Team the user wants to track
        target_rank (int): Desired rank (e.g., top 4 = 4)
        fixed_outcomes (dict): Forced outcomes, e.g., {"Arsenal vs Man City": "home"}
        num_simulations (int): Number of Monte Carlo runs (default = 10,000)

    Returns:
        float: Estimated probability of the user scenario happening
    """

    # load match odds from cached_odds.json via get_odds
    odds_data = get_odds()

    # load current standings and fixtures from solver
    base_table, fixtures = load_current_state(standings_df, fixtures_df)

    # create the user goal check function (e.g., "Arsenal finishes top 4")
    user_goal_check = make_user_goal_check(target_team, target_rank)

    success_count = 0

    # run the simulations
    for i in range(num_simulations):
        success = simulate_remaining_season(odds_data, base_table, fixtures, user_goal_check, fixed_outcomes)
        if success:
            success_count += 1

    # calculate the probability as number of successes over total sims
    probability = success_count / num_simulations

    # print the result (can return it for downstream use)
    print(f"Probability of {target_team} finishing top {target_rank}: {probability:.4f}")

    return probability, odds_data



def load_current_state(standings_df, fixtures_df):
    """
    Uses standings_df and fixtures_df to prepare data for Monte Carlo.

    Returns:
        base_table (dict): Current standings as {team: {points, position}}
        fixtures (list): Remaining matches as (home_team, away_team)
    """

    # build base_table from standings_df
    base_table = {
        row["team_name"]: {
            "points": row["points"],
            "position": row["position"]
        }
        for _, row in standings_df.iterrows()
    }

    # build fixtures list from fixtures_df (only games left to play)
    fixtures = [
        (row["home_team_name"], row["away_team_name"])
        for _, row in fixtures_df.iterrows()
        if row["status"] == "SCHEDULED"
    ]

    return base_table, fixtures


def apply_simulation(base_table, simulated_results, fixed_outcomes):
    """
    Applies simulated results and user constraints to the base league table.

    Args:
        base_table (dict): Current standings {team: {points, position, goal_difference (optional)}}
        simulated_results (dict): Random simulated match outcomes
        fixed_outcomes (dict): User-forced outcomes, e.g., {"Arsenal vs Man City": "home"}

    Returns:
        sim_table (dict): Final standings with updated points and positions
    """

    # make a copy of base_table to not overwrite original
    sim_table = {team: data.copy() for team, data in base_table.items()}

    # apply results to the sim_table
    for match_key, outcome in simulated_results.items():
        # if user has fixed outcome for this match, use it
        if match_key in fixed_outcomes:
            result = fixed_outcomes[match_key]
        else:
            result = outcome

        home, away = match_key.split(" vs ")

        # assign points based on result
        if result == "home":
            sim_table[home]["points"] += 3
        elif result == "away":
            sim_table[away]["points"] += 3
        elif result == "draw":
            sim_table[home]["points"] += 1
            sim_table[away]["points"] += 1
        else:
            raise ValueError(f"Unknown result: {result}")

    # sort league by points (and goal difference if available)
    sorted_teams = sorted(sim_table.items(),
                          key=lambda x: (-x[1]["points"], -x[1].get("goal_difference", 0)))

    # assign new positions
    for pos, (team, data) in enumerate(sorted_teams, start=1):
        sim_table[team]["position"] = pos

    return sim_table


def save_sim(data, filename):
    ensure_folder_exists(filename)
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

def load_sim(filename):
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)
    else:
        return None

def get_cache_filename(target_team, target_rank, fixed_outcomes_mc):
    key_string = json.dumps({
        "team": target_team,
        "rank": target_rank,
        "fixed_outcomes": fixed_outcomes_mc
    }, sort_keys=True)

    key_hash = hashlib.md5(key_string.encode()).hexdigest()

    return f"cache/monte_carlo_{key_hash}.pkl"


def ensure_folder_exists(filepath):
    folder = os.path.dirname(filepath)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
