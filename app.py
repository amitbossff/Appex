from flask import Flask, request, jsonify, send_file
from google_play_scraper import reviews, Sort
from datetime import datetime, date
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)

# ---------- HOME ----------
@app.route("/")
def home():
    return send_file("pdf1.html")


# ---------- REVIEWS API ----------
@app.route("/reviews")
def get_reviews():
    link = request.args.get("link", "").strip()
    date_str = request.args.get("date", "").strip()

    if not link or not date_str:
        return jsonify({"status": "error", "message": "Input required", "data": []})

    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    if target_date > date.today():
        return jsonify({"status": "error", "message": "Future date not allowed", "data": []})

    app_id = link.split("id=")[1].split("&")[0] if "id=" in link else link

    result, _ = reviews(
        app_id,
        lang="en",
        country="in",
        sort=Sort.NEWEST,
        count=15000
    )

    data, seen = [], set()

    for r in result:
        if r.get("at") and r["at"].date() == target_date:
            name = r.get("userName", "").strip()
            if name and name not in seen:
                seen.add(name)
                data.append({
                    "user": name,
                    "review": r.get("content", "")
                })

    return jsonify({
        "status": "success",
        "count": len(data),
        "data": data
    })


# ---------- PDF ----------
@app.route("/reviews-pdf")
def reviews_pdf():
    link = request.args.get("link")
    date_str = request.args.get("date")

    app_id = link.split("id=")[1].split("&")[0] if "id=" in link else link
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    result, _ = reviews(app_id, lang="en", country="in", sort=Sort.NEWEST, count=15000)

    names, seen = [], set()
    for r in result:
        if r.get("at") and r["at"].date() == target_date:
            n = r.get("userName")
            if n not in seen:
                seen.add(n)
                names.append(n)

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    y = h - 50
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Play Store Review Names")
    y -= 20
    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, y, f"Date: {date_str}")
    pdf.drawString(350, y, f"Total: {len(names)}")
    y -= 30

    for i, name in enumerate(names, 1):
        if y < 50:
            pdf.showPage()
            y = h - 50
        pdf.drawString(50, y, f"{i}. {name}")
        y -= 16

    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True,
                     download_name="playstore_reviews.pdf",
                     mimetype="application/pdf")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
