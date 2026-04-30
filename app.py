"""
ACEest Fitness & Gym - Flask Web Application
Version: 3.2.4
Flask wrapper exposing core business logic as REST API for CI/CD pipeline.
"""

from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime, date

app = Flask(__name__)
DB_NAME = "aceest_fitness.db"
APP_VERSION = "3.2.4"

PROGRAM_TEMPLATES = {
    "Fat Loss": ["Full Body HIIT", "Circuit Training", "Cardio + Weights"],
    "Muscle Gain": ["Push/Pull/Legs", "Upper/Lower Split", "Full Body Strength"],
    "Beginner": ["Full Body 3x/week", "Light Strength + Mobility"]
}


# ---------- DATABASE ----------
def init_db(db_name=DB_NAME):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY, password TEXT, role TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE, age INTEGER, height REAL, weight REAL,
        program TEXT, calories INTEGER, target_weight REAL,
        membership_status TEXT, membership_end TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT, date TEXT, workout_type TEXT,
        duration_min INTEGER, notes TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT, date TEXT, weight REAL, waist REAL, bodyfat REAL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT, week TEXT, adherence INTEGER)""")
    cur.execute("SELECT * FROM users WHERE username='admin'")
    if not cur.fetchone():
        cur.execute("INSERT INTO users VALUES ('admin','admin123','Admin')")
    conn.commit()
    conn.close()


def get_db(db_name=None):
    if db_name is None:
        import app as _app
        db_name = _app.DB_NAME
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn


# ---------- ROUTES ----------

@app.route("/")
def index():
    return jsonify({"app": "ACEest Fitness & Gym", "version": APP_VERSION, "status": "running"})


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "version": APP_VERSION}), 200


@app.route("/version")
def version():
    return jsonify({"version": APP_VERSION}), 200


@app.route("/clients", methods=["GET"])
def get_clients():
    conn = get_db()
    clients = conn.execute("SELECT * FROM clients ORDER BY name").fetchall()
    conn.close()
    return jsonify([dict(c) for c in clients]), 200


@app.route("/clients", methods=["POST"])
def add_client():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    for field in ["name", "age", "weight", "height"]:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
    conn = get_db()
    try:
        conn.execute("""INSERT INTO clients
            (name, age, weight, height, program, calories, target_weight, membership_status, membership_end)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (data["name"], int(data["age"]), float(data["weight"]), float(data["height"]),
             data.get("program", "Beginner"), int(data.get("calories", 2000)),
             float(data.get("target_weight", data["weight"])),
             data.get("membership_status", "Active"), data.get("membership_end", "")))
        conn.commit()
        return jsonify({"message": "Client added successfully", "name": data["name"]}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Client already exists"}), 409
    finally:
        conn.close()


@app.route("/clients/<name>", methods=["GET"])
def get_client(name):
    conn = get_db()
    client = conn.execute("SELECT * FROM clients WHERE name=?", (name,)).fetchone()
    conn.close()
    if client:
        return jsonify(dict(client)), 200
    return jsonify({"error": "Client not found"}), 404


@app.route("/clients/<name>", methods=["DELETE"])
def delete_client(name):
    conn = get_db()
    conn.execute("DELETE FROM clients WHERE name=?", (name,))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Client '{name}' deleted"}), 200


@app.route("/workouts", methods=["GET"])
def get_workouts():
    conn = get_db()
    workouts = conn.execute("SELECT * FROM workouts ORDER BY date DESC").fetchall()
    conn.close()
    return jsonify([dict(w) for w in workouts]), 200


@app.route("/workouts", methods=["POST"])
def add_workout():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    for field in ["client_name", "workout_type", "duration_min"]:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
    conn = get_db()
    conn.execute("""INSERT INTO workouts (client_name, date, workout_type, duration_min, notes)
        VALUES (?, ?, ?, ?, ?)""",
        (data["client_name"], data.get("date", date.today().isoformat()),
         data["workout_type"], int(data["duration_min"]), data.get("notes", "")))
    conn.commit()
    conn.close()
    return jsonify({"message": "Workout logged successfully"}), 201


@app.route("/metrics", methods=["POST"])
def add_metrics():
    data = request.get_json()
    if not data or "client_name" not in data:
        return jsonify({"error": "Missing client_name"}), 400
    conn = get_db()
    conn.execute("""INSERT INTO metrics (client_name, date, weight, waist, bodyfat)
        VALUES (?, ?, ?, ?, ?)""",
        (data["client_name"], data.get("date", date.today().isoformat()),
         float(data.get("weight", 0)), float(data.get("waist", 0)), float(data.get("bodyfat", 0))))
    conn.commit()
    conn.close()
    return jsonify({"message": "Metrics saved"}), 201


@app.route("/programs", methods=["GET"])
def get_programs():
    return jsonify(PROGRAM_TEMPLATES), 200


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No credentials provided"}), 400
    conn = get_db()
    user = conn.execute(
        "SELECT role FROM users WHERE username=? AND password=?",
        (data.get("username", ""), data.get("password", ""))
    ).fetchone()
    conn.close()
    if user:
        return jsonify({"message": "Login successful", "role": user["role"]}), 200
    return jsonify({"error": "Invalid credentials"}), 401


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
