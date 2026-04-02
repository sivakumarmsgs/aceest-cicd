"""
ACEest Fitness & Gym - Flask Web Application
DevOps Assignment - CI/CD Pipeline Implementation
"""

from flask import Flask, jsonify, request

app = Flask(__name__)

# ---------- In-memory data store ----------
clients = {}

PROGRAMS = {
    "Fat Loss": {"calorie_factor": 22, "workout": "HIIT + Cardio"},
    "Muscle Gain": {"calorie_factor": 35, "workout": "Push/Pull/Legs"},
    "Beginner": {"calorie_factor": 26, "workout": "Full Body 3x/week"},
}


# ---------- Helper ----------
def calculate_calories(weight_kg: float, program: str) -> int:
    """Calculate daily calorie target based on weight and program."""
    if program not in PROGRAMS:
        return 0
    return int(weight_kg * PROGRAMS[program]["calorie_factor"])


# ---------- Routes ----------
@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "app": "ACEest Fitness & Gym",
        "version": "3.2.4",
        "status": "running",
    })


@app.route("/programs", methods=["GET"])
def get_programs():
    """Return all available fitness programs."""
    return jsonify({"programs": list(PROGRAMS.keys())})


@app.route("/clients", methods=["GET"])
def get_clients():
    """Return all registered clients."""
    return jsonify({"clients": list(clients.values())})


@app.route("/clients", methods=["POST"])
def add_client():
    """Register a new client."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    name = data.get("name", "").strip()
    program = data.get("program", "").strip()
    weight = data.get("weight_kg", 0)
    age = data.get("age", 0)

    if not name:
        return jsonify({"error": "Name is required"}), 400
    if not program or program not in PROGRAMS:
        return jsonify({"error": f"Program must be one of: {list(PROGRAMS.keys())}"}), 400
    if not isinstance(weight, (int, float)) or weight <= 0:
        return jsonify({"error": "Valid weight_kg is required"}), 400
    if name in clients:
        return jsonify({"error": f"Client '{name}' already exists"}), 409

    calories = calculate_calories(weight, program)
    client = {
        "name": name,
        "age": age,
        "weight_kg": weight,
        "program": program,
        "calories": calories,
        "workout": PROGRAMS[program]["workout"],
        "membership_status": "Active",
    }
    clients[name] = client
    return jsonify({"message": "Client added", "client": client}), 201


@app.route("/clients/<name>", methods=["GET"])
def get_client(name):
    """Fetch a single client by name."""
    client = clients.get(name)
    if not client:
        return jsonify({"error": "Client not found"}), 404
    return jsonify(client)


@app.route("/clients/<name>", methods=["DELETE"])
def delete_client(name):
    """Remove a client."""
    if name not in clients:
        return jsonify({"error": "Client not found"}), 404
    clients.pop(name)
    return jsonify({"message": f"Client '{name}' deleted"})


@app.route("/clients/<name>/progress", methods=["POST"])
def log_progress(name):
    """Log weekly adherence for a client."""
    if name not in clients:
        return jsonify({"error": "Client not found"}), 404
    data = request.get_json()
    adherence = data.get("adherence", 0)
    if not (0 <= adherence <= 100):
        return jsonify({"error": "Adherence must be 0-100"}), 400
    clients[name]["last_adherence"] = adherence
    return jsonify({"message": "Progress logged", "adherence": adherence})


@app.route("/calories", methods=["GET"])
def calorie_calculator():
    """Quick calorie estimate via query params."""
    weight = request.args.get("weight", type=float)
    program = request.args.get("program", "")
    if not weight or not program:
        return jsonify({"error": "Provide weight and program query params"}), 400
    calories = calculate_calories(weight, program)
    if calories == 0:
        return jsonify({"error": "Invalid program"}), 400
    return jsonify({"weight_kg": weight, "program": program, "calories": calories})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
