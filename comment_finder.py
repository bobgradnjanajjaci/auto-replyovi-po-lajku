import re
import time
import requests

HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

# Ključne riječi za tvoju knjigu
REQUIRED_PHRASES = [
    "virexon cycle",
    "virexoncycle",
    "dalen korvik",
    "virexon",
    "knjiga"
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
    for _ in range(3): # Gledamo 3 stranice komentara
        try:
            r = _session.get(
                "https://www.tiktok.com/api/comment/list/",
                headers=HEADERS,
                params={"aid": 1988, "count": 50, "cursor": cursor, "aweme_id": video_id},
                timeout=7,
            )
            data = r.json()
            batch = data.get("comments") or []
            comments.extend(batch)
            if not data.get("has_more"): break
            cursor = int(data.get("cursor") or 0)
        except: break
    return comments

def pick_best_comment(comments):
    """Bira komentar sa NAJVIŠE LAJKOVA koji pominje knjigu[cite: 3]"""
    best = None
    max_likes = -1

    for c in comments[:80]: 
        text = c.get("text") or ""
        likes = int(c.get("digg_count") or 0)
        
        if not has_target_phrase(text):
            continue

        # Promjena logike: Tražimo najviše lajkova umjesto reply-ova[cite: 3]
        if likes > max_likes:
            max_likes = likes
            best = {
                "cid": c.get("cid"),
                "likes": likes,
                "username": c.get("user", {}).get("unique_id"),
                "text": text
            }
    return best

def build_comment_link(video_url: str, video_id: str, cid: str) -> str:
    """Generiše mobilni format linka koji paneli traže"""
    return f"https://www.tiktok.com/@user/video/{video_id}?is_copy_url=1&is_from_webapp=1&item_id={video_id}&cid={cid}"

def find_target_comment(video_url: str) -> dict:
    video_id = extract_video_id(video_url)
    if not video_id: return {"found": False}

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
    return {"found": False}