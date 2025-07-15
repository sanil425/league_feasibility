import os
import requests
import json
from dotenv import load_dotenv

# Load API keys from the .env file
load_dotenv()
API_KEY = os.getenv("ODDS_API_KEY")

def get_odds(save_to_file=True):
    """
    Fetches current Premier League match odds from OddsAPI and converts them to normalized probabilities.

    Args:
        save_to_file (bool): If True, saves the odds to data/cached_odds.json.

    Returns:
        dict: A dictionary of match odds and probabilities.
    """
    SPORT = 'soccer_epl'   # Premier League
    REGION = 'uk'          # Use UK bookmakers
    MARKET = 'h2h'         # Head-to-head (Win/Draw/Loss)

    url = f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds'

    params = {
        'apiKey': API_KEY,
        'regions': REGION,
        'markets': MARKET,
        'oddsFormat': 'decimal',
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code}, {response.text}")

    data = response.json()
    odds_data = {}

    for match in data:
        home_team = match['home_team']
        away_team = match['away_team']
        match_key = f"{home_team} vs {away_team}"

        # Get the first bookmaker's market
        bookmakers = match['bookmakers']
        if not bookmakers:
            continue  # Skip matches with no bookmaker data

        bookmaker = bookmakers[0]               # First bookmaker
        markets = bookmaker['markets']
        if not markets:
            continue  # Skip if no market data

        market = markets[0]                     # First market (should be 'h2h')

        # Extract odds for home win, draw, and away win
        raw_odds = {}
        for outcome in market['outcomes']:
            if outcome['name'] == home_team:
                raw_odds['home'] = outcome['price']
            elif outcome['name'] == away_team:
                raw_odds['away'] = outcome['price']
            elif outcome['name'].lower() == 'draw':
                raw_odds['draw'] = outcome['price']

        # Only process matches with complete odds
        if set(raw_odds.keys()) != {'home', 'draw', 'away'}:
            continue  # Skip incomplete data

        # Convert odds to normalized probabilities
        probs = convert_to_probabilities(raw_odds)

        # Store in dictionary
        odds_data[match_key] = {
            'odds': raw_odds,
            'probabilities': probs
        }

    # Save to local JSON
    if save_to_file:
        os.makedirs('data', exist_ok=True)
        with open('data/cached_odds.json', 'w') as f:
            json.dump(odds_data, f, indent=4)

    return odds_data


def convert_to_probabilities(odds):
    """
    Converts decimal odds to implied probabilities, normalized to sum to 1.

    Args:
        odds (dict): 'home', 'draw', 'away' odds.

    Returns:
        dict: Normalized probabilities.
    """
    raw_probs = {k: 1 / v for k, v in odds.items()}
    total = sum(raw_probs.values())
    return {k: v / total for k, v in raw_probs.items()}


if __name__ == "__main__":
    # Run this file directly to test
    odds = get_odds()

    for match, info in odds.items():
        print(f"{match}: {info['probabilities']}")
