from fastapi import FastAPI
from forexfactory_scraper import fetch_and_parse_xml

app = FastAPI()

# This variable keeps the last successful data in memory
last_data = []

@app.get("/calendar")
def get_calendar():
    global last_data
    events = fetch_and_parse_xml()
    
    if events:
        # If we got data, save it as the new "last_data"
        last_data = events
        return {"success": True, "data": events}
    else:
        # If scraper failed, return the cached data instead
        return {"success": True, "data": last_data, "note": "cached"}
