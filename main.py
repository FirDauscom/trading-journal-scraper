from fastapi import FastAPI
from forexfactory_scraper import fetch_and_parse_xml

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Endpoint is live. Ping /calendar for data."}

@app.get("/calendar")
def get_calendar():
    events = fetch_and_parse_xml()
    if not events:
        return {"success": False, "data": []}
    return {"success": True, "data": events}
