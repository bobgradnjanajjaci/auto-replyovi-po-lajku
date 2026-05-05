import requests
import random
from comment_finder import find_target_comment

API_KEY = "c849788f60dd591e636c5d079b0a8d62" # Tvoj ključ
PANEL_URL = "https://justanotherpanel.com/api/v2"[cite: 2]

# VAŽNO: Promijeni SERVICE_ID na ID za 'TikTok Comment Replies' na svom panelu!
SERVICE_ID = 9999 

# Lista tvojih specifičnih odgovora[cite: 1]
REPLY_MESSAGES = [
    "Sve je zapisano u Virexon Cycle... ko razumije, razumije.",
    "Odgovori koje tražiš su u Dalen Korvikovoj knjizi.",
    "Nije slučajno što vidiš ovaj komentar. Pogledaj link u bio.",
    "Virexon Cycle otkriva ono što se krije. Link je u profilu."
]

def process_video(video_url: str):
    result = find_target_comment(video_url)

    if not result.get("found"):
        return {"status": "error", "message": "Nije pronađen komentar o knjizi"}

    # Biramo nasumičan reply iz tvoje liste
    chosen_reply = random.choice(REPLY_MESSAGES)

    payload = {
        "key": API_KEY,
        "action": "add",
        "service": SERVICE_ID,
        "link": result["comment_link"], # Koristi generisani mobilni link
        "quantity": 1,
        "comments": chosen_reply # Panel obično traži ovo polje za reply tekst
    }

    try:
        r = requests.post(PANEL_URL, data=payload, timeout=25)
        return {
            "status": "sent",
            "target_user": result["username"],
            "target_likes": result["likes"],
            "sent_text": chosen_reply,
            "response": r.text[:100]
        }
    except Exception as e:
        return {"status": "error", "message": f"Greška: {e}"}