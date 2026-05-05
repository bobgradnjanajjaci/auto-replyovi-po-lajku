import re
import time
import requests

# Poboljšani Headeri da simuliramo pravi browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.tiktok.com/"
}

# Sve varijacije iz tvog primera
REQUIRED_PHRASES = [
    "virexon cycle",
    "dalen korvik",
]

_session = requests.Session()

def normalize(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def has_target_phrase(text: str) -> bool:
    norm = normalize(text)
    return any(phrase in norm for phrase in REQUIRED_PHRASES)

def extract_video_id(url: str):
    m = re.search(r"/video/(\d+)", url)
    return m.group(1) if m else None

def fetch_comments(video_id: str):
    comments = []
    cursor = 0
    print(f"--- ZAPOČINJEM SKENIRANJE VIDEA: {video_id} ---")
    
    for i in range(50): # Skenira do 2500 komentara
        try:
            r = _session.get(
                "https://www.tiktok.com/api/comment/list/",
                headers=HEADERS,
                params={"aid": 1988, "count": 50, "cursor": cursor, "aweme_id": video_id},
                timeout=12,
            )
            
            if r.status_code != 200:
                print(f"Greška na stranici {i}: Status {r.status_code}")
                break

            data = r.json()
            batch = data.get("comments") or []
            
            print(f"Stranica {i}: Primljeno {len(batch)} komentara")
            
            if not batch:
                break

            comments.extend(batch)

            if not data.get("has_more"):
                break
            
            cursor = int(data.get("cursor") or 0)
            time.sleep(0.4) # Pauza da izbegnemo blokadu
            
        except Exception as e:
            print(f"Greška u konekciji na stranici {i}: {e}")
            break
            
    print(f"UKUPNO SKUPLJENO: {len(comments)} komentara.")
    return comments

def pick_best_comment(comments):
    best = None
    max_likes = -1
    match_count = 0

    for c in comments: 
        try:
            text = c.get("text") or ""
            likes = int(c.get("digg_count") or 0)
            
            if not has_target_phrase(text):
                continue

            match_count += 1
            if likes > max_likes:
                max_likes = likes
                best = {
                    "cid": c.get("cid"),
                    "likes": likes,
                    "username": c.get("user", {}).get("unique_id"),
                    "text": text,
                }
        except:
            continue
            
    print(f"PRONAĐENO KOMENTARA KOJI SE POKLAPAJU SA KNJIGOM: {match_count}")
    return best

def build_comment_link(video_url: str, video_id: str, cid: str) -> str:
    # Mobilni format linka neophodan za panel[cite: 3]
    return f"https://www.tiktok.com/@user/video/{video_id}?is_copy_url=1&is_from_webapp=1&item_id={video_id}&cid={cid}"

def find_target_comment(video_url: str) -> dict:
    video_id = extract_video_id(video_url)
    if not video_id:
        return {"found": False, "reason": "invalid_url"}

    comments = fetch_comments(video_id)
    best = pick_best_comment(comments)

    if best:
        return {
            "found": True,
            "comment_link": build_comment_link(video_url, video_id, best["cid"]),
            "likes": best["likes"],
            "username": best["username"],
            "text": best["text"]
        }
    
    return {"found": False, "reason": "no_keyword_match"}
