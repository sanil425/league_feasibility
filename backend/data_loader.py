import json
import os

# helper function to load JSON file
def load_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def load_data(dummy=True):
    """
    Loads data from the data directory.
    If dummy is True, loads dummy data, otherwise loads real data.
    Returns standings and fixtures data.
    """
    # absolute path to data directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")

    if dummy:
        standings_file = os.path.join(data_dir, "dummy_prem_standings.json")
        fixtures_file = os.path.join(data_dir, "dummy_prem_fixtures.json")
        print("Loaded dummy data")
    else:
        standings_file = os.path.join(data_dir, "prem_standings.json")
        fixtures_file = os.path.join(data_dir, "prem_fixtures.json")
        print("Loaded real data")
    
    # load JSON files
    standings = load_json(standings_file)
    fixtures = load_json(fixtures_file)

    return standings, fixtures


    


