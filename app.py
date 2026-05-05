from flask import Flask, request, render_template_string
import time
from auto_brain_core import process_video

app = Flask(__name__)

# Tvoj interfejs sa tamnom temom[cite: 1]
HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Virexon Auto-Reply Bot</title>
  <style>
    body{font-family:system-ui;background:#0b1220;color:#e5e7eb;display:flex;justify-content:center;padding:24px}
    .card{width:100%;max-width:900px;background:#0f172a;border:1px solid #334155;border-radius:16px;padding:24px}
    textarea{width:100%;min-height:220px;background:#0b1220;color:#e5e7eb;border:1px solid #334155;border-radius:12px;padding:12px;font-family:monospace}
    button{margin-top:15px;padding:12px 24px;border-radius:999px;border:none;background:#6366f1;color:white;font-weight:700;cursor:pointer;width:100%}
    pre{white-space:pre-wrap;background:#0b1220;border:1px solid #334155;border-radius:12px;padding:12px;margin-top:20px;font-size:13px}
  </style>
</head>
<body>
  <div class="card">
    <h2>Virexon Cycle Auto-Reply Bot ⚡</h2>
    <p>Unesi TikTok linkove (jedan po liniji):</p>
    <form method="post">
      <textarea name="links" placeholder="https://www.tiktok.com/..."></textarea>
      <button type="submit">Pokreni Automatizaciju</button>
    </form>
    {% if log %}
      <pre>{{log}}</pre>
    {% endif %}
  </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    logs = []
    if request.method == "POST":
        links_text = request.form.get("links","")
        raw_links = [l.strip() for l in links_text.splitlines() if l.strip()]

        for idx, url in enumerate(raw_links, start=1):
            res = process_video(url)
            logs.append(f"[{idx}] {url} -> {res}")
            time.sleep(2) # Mala pauza između linkova

    return render_template_string(HTML, log="\n".join(logs))

if __name__ == "__main__":
    app.run(debug=True)