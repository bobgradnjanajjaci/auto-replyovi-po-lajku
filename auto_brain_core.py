import requests
import random
from comment_finder import find_target_comment

# Tvoji novi kredencijali za panel
API_KEY = "b9b7a1a6142778498309844dfb0103c0"
PANEL_URL = "https://topsfollows.com/api/v2"
SERVICE_ID = 1232

# Tekstovi koje si naveo za reply
REPLY_MESSAGES = [
    "For me its scary how much power this book has. I felt like someone had reached into my head and exposed everything about how are we controlled and how to actually leave this cycle",
    "I saw that this book was removed a few time, and there are rumors that the author is part of some high tier people. It really revealed too much..."
]

def process_video(video_url: str):
    # Pronalazimo najbolji komentar koji pominje knjigu (sa najviše lajkova)
    result = find_target_comment(video_url)

    if not result.get("found"):
        return {"status": "error", "message": "Nije pronađen adekvatan komentar"}

    # Biramo jedan od tvoja dva ponuđena teksta
    chosen_reply = random.choice(REPLY_MESSAGES)

    # Priprema podataka za slanje na panel[cite: 2]
    payload = {
        "key": API_KEY,
        "action": "add",
        "service": SERVICE_ID,
        "link": result["comment_link"], # Skripta ovdje šalje mobilni link komentara
        "quantity": 1,
        "comments": chosen_reply
    }

    try:
        # Slanje zahtjeva na TopsFollows API
        r = requests.post(PANEL_URL, data=payload, timeout=25)
        
        # Logovanje rezultata za pregled u app.py
        return {
            "status": "sent",
            "target_user": result["username"],
            "target_likes": result["likes"],
            "sent_text": chosen_reply[:50] + "...",
            "api_response": r.text[:150]
        }
    except Exception as e:
        return {"status": "error", "message": f"Panel Connection Error: {e}"}
