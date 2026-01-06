from flask import Flask, request, jsonify, send_file
from google_play_scraper import reviews, Sort
import uuid
import os

app = Flask(__name__)

TOKEN_STORE = {}

@app.route("/")
def home():
    return send_file("index.html")

@app.route("/reviews")
def get_reviews():
    app_link = request.args.get("link")
    token_id = request.args.get("token_id")

    if not app_link or "id=" not in app_link:
        return jsonify({"reviews": [], "token_id": None})

    try:
        app_id = app_link.split("id=")[1].split("&")[0]
        continuation_token = TOKEN_STORE.get(token_id)

        result, new_token = reviews(
            app_id,
            lang="en",
            country="in",
            sort=Sort.NEWEST,
            count=100,
            continuation_token=continuation_token
        )

        output = []
        for r in result:
            output.append({
                "user": r.get("userName", ""),
                "rating": r.get("score", ""),
                "date": r["at"].strftime("%Y-%m-%d") if r.get("at") else "",
                "review": r.get("content", "")
            })

        next_token_id = None
        if new_token:
            next_token_id = str(uuid.uuid4())
            TOKEN_STORE[next_token_id] = new_token

        return jsonify({"reviews": output, "token_id": next_token_id})

    except Exception as e:
        print("Error:", e)
        return jsonify({"reviews": [], "token_id": None})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
