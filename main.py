import os
import re
from datetime import datetime, timezone
from forexfactory_scraper import fetch_and_parse_xml
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def clean_num(val):
    if not val or val == 'None' or val == '': 
        return None
    cleaned = re.sub(r'[^\d.-]', '', str(val))
    return float(cleaned) if cleaned else None

def main():
    print("Fetching data from Forex Factory...")
    events = fetch_and_parse_xml()
    
    if not events:
        print("No events found.")
        return
        
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    formatted_records = []
    
    for ev in events:
        raw_date = ev.get('date', '') 
        raw_time = ev.get('time', '') 
        
        # Safely handle time
        time_str = raw_time.replace('am', ' AM').replace('pm', ' PM') if raw_time else "12:00 AM"
        if "Day" in time_str or not time_str.strip():
            time_str = "12:00 AM"
            
        try:
            # Convert Forex Factory time to standard database time
            dt = datetime.strptime(f"{raw_date} {time_str}", "%m-%d-%Y %I:%M %p")
            iso_date = dt.isoformat() + "Z"
        except Exception:
            # If date format is weird, fallback to current time so it doesn't crash
            iso_date = datetime.now(timezone.utc).isoformat() + "Z"
            
        formatted_records.append({
            "event_date": iso_date,
            "country": ev.get('currency', 'None'),
            "currency": ev.get('currency', 'None'),
            "event_name": ev.get('title', 'Unknown'),
            "estimate": clean_num(ev.get('forecast')),
            "previous": clean_num(ev.get('previous')),
            "actual": clean_num(ev.get('actual')),
            "impact": ev.get('impact', 'None')
        })

    print(f"Pushing {len(formatted_records)} events to Supabase...")
    supabase.table("economic_calendar").upsert(
        formatted_records, 
        on_conflict="event_date,country,event_name"
    ).execute()
    print("Success!")

if __name__ == "__main__":
    main()
