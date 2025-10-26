from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)

DB_FILE = "data.db"

# --- Create table if not exists ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    goals INTEGER,
                    assists INTEGER,
                    match_date TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# --- Helper: get last 2 Fridays ---
def get_last_two_fridays():
    today = datetime.now()
    days_since_friday = (today.weekday() - 4) % 7
    last_friday = today - timedelta(days=days_since_friday)
    prev_friday = last_friday - timedelta(days=7)
    return [last_friday.strftime("%d %B %Y"), prev_friday.strftime("%d %B %Y")]

# --- Main form ---
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", fridays=get_last_two_fridays())

# --- Handle form submission ---
@app.route("/submit", methods=["POST"])
def submit():
    try:
        data = request.get_json()
        name = data.get("name")
        goals = data.get("goals")
        assists = data.get("assists")
        match_date = data.get("match_date")

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "INSERT INTO submissions (name, goals, assists, match_date) VALUES (?, ?, ?, ?)",
            (name, goals, assists, match_date),
        )
        conn.commit()
        conn.close()

        return jsonify({"success": True})

    except Exception as e:
        print("Error inserting data:", e)
        return jsonify({"success": False, "error": str(e)})

# --- Admin page to view results ---
@app.route("/submissions")
def submissions():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM submissions ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return render_template("submissions.html", data=rows)

if __name__ == "__main__":
    app.run(debug=True)
