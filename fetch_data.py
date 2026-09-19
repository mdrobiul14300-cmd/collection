import json
import os
import requests

BASE_URL = "https://streamed.pk/api"

def fetch_json(url):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():
    print("Fetching live matches...")
    matches = fetch_json(f"{BASE_URL}/matches/live")
    
    if not matches:
        print("No live matches found or failed to fetch.")
        matches = []

    detailed_matches = []

    for match in matches:
        match_data = match.copy()
        match_data["streams"] = []
        
        # Each match has stream sources
        sources = match.get("sources", [])
        for source in sources:
            src_name = source.get("source")
            src_id = source.get("id")
            
            if src_name and src_id:
                stream_url = f"{BASE_URL}/stream/{src_name}/{src_id}"
                streams = fetch_json(stream_url)
                if streams:
                    match_data["streams"].extend(streams)
        
        detailed_matches.append(match_data)

    # Save data to data.json
    output_filename = "data.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(detailed_matches, f, indent=4, ensure_ascii=False)
    
    print(f"Successfully saved {len(detailed_matches)} matches to {output_filename}")

if __name__ == "__main__":
    main():
