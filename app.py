from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import csv
import os

app = Flask(__name__)

CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "submissions.csv")
print("Saving CSV to:", CSV_FILE)
print("Writable:", os.access(os.path.dirname(CSV_FILE), os.W_OK))


# --- Create CSV file with headers if it doesn't exist ---
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Goals", "Assists", "Match Date", "Timestamp"])

# --- Helper: last two Fridays ---
def get_last_two_fridays():
    today = datetime.now()
    days_since_friday = (today.weekday() - 4) % 7
    last_friday = today - timedelta(days=days_since_friday)
    prev_friday = last_friday - timedelta(days=7)
    return [last_friday.strftime("%d %B %Y"), prev_friday.strftime("%d %B %Y")]

@app.route("/")
def index():
    return render_template("index.html", fridays=get_last_two_fridays())

@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()
    name = data.get("name", "").strip()
    goals = data.get("goals", "")
    assists = data.get("assists", "")
    match_date = data.get("match_date", "")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Append the data to CSV
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([name, goals, assists, match_date, timestamp])

    return jsonify({"success": True})

@app.route("/submissions")
def submissions():
    rows = []
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        rows = list(reader)
    return render_template("submissions.html", data=rows)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

from flask import send_file

# 🔒 Replace this with your private key (choose anything unique)
ADMIN_KEY = "olly"

@app.route("/download")
def download_csv():
    key = request.args.get("key")
    if key != ADMIN_KEY:
        return "Unauthorized", 403

    if not os.path.exists(CSV_FILE):
        return "No submissions yet", 404

    return send_file(CSV_FILE, as_attachment=True)
