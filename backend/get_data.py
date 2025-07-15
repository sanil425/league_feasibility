import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BASE_URL = "https://api.football-data.org/v4/competitions/PL" # access premier league data

headers = {
    "X-Auth-Token": FOOTBALL_DATA_API_KEY # required API key for football data
}

# function to fetch standings data
def get_standings():
    url = f"{BASE_URL}/standings" # API endpoint for standings

    response = requests.get(url, headers=headers) # GET request to API

    if response.status_code != 200: # check errors
        print(f"Error fetching standings: {response.status_code}")
        return None

    data = response.json() # parse response

    with open("data/prem_standings.json", "w") as f:
        json.dump(data, f, indent=4)

    print("Premier League standings saved to data/prem_standings.json")


def get_fixtures():
    url = f"{BASE_URL}/matches?status=SCHEDULED" # API endpoint for fixtures

    response = requests.get(url, headers=headers) # GET request to API

    if response.status_code != 200: # check errors
        print(f"Error fetching fixtures: {response.status_code}")
        return None
    
    data = response.json() # parse response
    
    with open("data/prem_fixtures.json", "w") as f:
        json.dump(data, f, indent=4)

    print("Premier League fixtures saved to data/prem_fixtures.json")




if __name__ == "__main__":
    get_standings()
    get_fixtures()




