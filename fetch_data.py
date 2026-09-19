import json
import os
from datetime import datetime
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

def process_matches(matches_list):
    """ম্যাচের ডাটা প্রসেস করে স্ট্রিম এবং সময় যুক্ত করে"""
    if not matches_list:
        return []

    detailed_matches = []
    for match in matches_list:
        match_data = match.copy()
        
        # Unix timestamp (milliseconds) থেকে Readable Date-Time বের করা
        if "date" in match and match["date"]:
            timestamp = match["date"] / 1000.0
            match_data["formatted_time"] = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')

        # Stream Links সংগ্রহ করা
        match_data["streams"] = []
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
        
    return detailed_matches

def main():
    print("Fetching matches schedule and live data...")
    
    # ১. আজকের সব শিডিউল ম্যাচ (Today's Scheduled Matches)
    print("Fetching today's schedule...")
    today_matches = fetch_json(f"{BASE_URL}/matches/all-today")
    processed_today = process_matches(today_matches)

    # ২. বর্তমানে লাইভ চলা ম্যাচ (Live Matches)
    print("Fetching live matches...")
    live_matches = fetch_json(f"{BASE_URL}/matches/live")
    processed_live = process_matches(live_matches)

    # ৩. সব আপকামিং/অল ম্যাচ (All Scheduled Matches)
    print("Fetching all matches schedule...")
    all_matches = fetch_json(f"{BASE_URL}/matches/all")
    processed_all = process_matches(all_matches)

    # সব ডাটা একসাথে সাজানো
    final_data = {
        "last_updated": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
        "live_matches": processed_live,
        "today_schedule": processed_today,
        "all_schedule": processed_all
    }

    # Save data to data.json
    output_filename = "data.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=4, ensure_ascii=False)
    
    print(f"Successfully saved schedule & streams to {output_filename}")

if __name__ == "__main__":
    main()
