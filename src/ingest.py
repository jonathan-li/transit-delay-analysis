import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("BART_API_KEY")

if not API_KEY:
    raise ValueError("BART_API_KEY not set in environment or .env file")

BASE_URL = "https://api.bart.gov/api/etd.aspx"

def fetch_etd(station_abbr):
    params = {"cmd": "etd", "orig": station_abbr, "key": API_KEY, "json": 
"y"}
    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

def normalize_etd(raw_json):
    records = []
    station_list = raw_json.get("root", {}).get("station", [])
    if not station_list:
        return pd.DataFrame()
    station = station_list[0]
    for etd in station.get("etd", []):
        for est in etd.get("estimate", []):
            records.append({
                "station": station.get("name"),
                "abbr": station.get("abbr"),
                "destination": etd.get("destination"),
                "minutes": est.get("minutes"),
                "platform": est.get("platform"),
                "direction": est.get("direction"),
                "length": est.get("length"),
                "fetched_at": datetime.utcnow().isoformat()
            })
    return pd.DataFrame(records)

def save_data(df, station_abbr):
    os.makedirs("data/raw", exist_ok=True)
    filename = f"data/raw/etd_{station_abbr}_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.csv"
    df.to_csv(filename, index=False)
    print(f"Saved to {filename}")

def main():
    stations = ["12th", "16th", "mont"]
    for st in stations:
        raw = fetch_etd(st)
        df = normalize_etd(raw)
        if not df.empty:
            save_data(df, st)
        else:
            print(f"No data for {st}")

if __name__ == "__main__":
    main()

