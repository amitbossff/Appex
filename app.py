from flask import Flask, request, jsonify, send_file
from google_play_scraper import reviews, Sort
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return send_file("pdf1.html")

@app.route("/reviews")
def get_reviews():
    link = request.args.get("link", "").strip()
    date_str = request.args.get("date", "").strip()

    if not link or not date_str:
        return jsonify({"status": "error", "message": "Invalid input", "data": []})

    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        # extract app id
        if "id=" in link:
            app_id = link.split("id=")[1].split("&")[0]
        else:
            app_id = link

        result, _ = reviews(
            app_id,
            lang="en",
            country="in",
            sort=Sort.NEWEST,
            count=20000
        )

        data = []

        for r in result:
            if r.get("at") and r["at"].date() == target_date:
                text = r.get("content", "").strip()
                if text:
                    data.append({
                        "review": text,
                        "date": r["at"].strftime("%d %b %Y"),
                        "userName": r.get("userName", "Anonymous")
                    })

        return jsonify({
            "status": "success",
            "count": len(data),
            "data": data
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e), "data": []})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
