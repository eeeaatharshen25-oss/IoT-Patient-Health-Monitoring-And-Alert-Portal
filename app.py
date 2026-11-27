import os
import sqlite3
from datetime import datetime, timezone
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for, flash

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-only-change-me")
DB_PATH = os.getenv("DATABASE_PATH", "patient_monitor.db")
API_KEY = os.getenv("API_KEY", "change-this-api-key")

# Illustrative demo limits only; they are not clinical alarm thresholds.
DEMO_LIMITS = {
    "heart_rate": (50, 120),
    "spo2": (90, 100),
    "temperature": (35.0, 38.0),
}


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with connect_db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            notes TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            heart_rate REAL,
            spo2 REAL,
            temperature REAL,
            recorded_at TEXT NOT NULL,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            reading_id INTEGER,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(patient_id) REFERENCES patients(id),
            FOREIGN KEY(reading_id) REFERENCES readings(id)
        )""")
        if con.execute("SELECT COUNT(*) FROM patients").fetchone()[0] == 0:
            con.execute(
                "INSERT INTO patients(name, age, notes, created_at) VALUES (?, ?, ?, ?)",
                ("Demo Patient", 35, "Sample record for testing", now_iso())
            )


def require_device_key(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        supplied = request.headers.get("X-API-Key", "")
        if API_KEY in ("", "change-this-api-key") or supplied != API_KEY:
            return jsonify({"ok": False, "error": "Unauthorized. Configure API_KEY in .env and send X-API-Key."}), 401
        return fn(*args, **kwargs)
    return wrapper


def find_alerts(values):
    messages = []
    labels = {
        "heart_rate": ("Heart rate", "bpm"),
        "spo2": ("SpO2", "%"),
        "temperature": ("Temperature", "°C"),
    }
    for key, value in values.items():
        if value is None:
            continue
        low, high = DEMO_LIMITS[key]
        if value < low or value > high:
            label, unit = labels[key]
            messages.append(f"{label} reading {value:g} {unit} is outside the configured demo range ({low}–{high}).")
    return messages


@app.route("/")
def dashboard():
    with connect_db() as con:
        patients = con.execute("SELECT * FROM patients ORDER BY name").fetchall()
        patient_id = request.args.get("patient_id", type=int)
        if patient_id is None and patients:
            patient_id = patients[0]["id"]
        patient = con.execute("SELECT * FROM patients WHERE id=?", (patient_id,)).fetchone() if patient_id else None
        latest = con.execute(
            "SELECT * FROM readings WHERE patient_id=? ORDER BY id DESC LIMIT 1", (patient_id,)
        ).fetchone() if patient_id else None
        history = con.execute(
            "SELECT * FROM readings WHERE patient_id=? ORDER BY id DESC LIMIT 10", (patient_id,)
        ).fetchall() if patient_id else []
        alerts = con.execute(
            """SELECT a.*, p.name AS patient_name FROM alerts a
               JOIN patients p ON p.id=a.patient_id ORDER BY a.id DESC LIMIT 10"""
        ).fetchall()
    return render_template("dashboard.html", patients=patients, patient=patient,
                           latest=latest, history=history, alerts=alerts)


@app.route("/patients", methods=["GET", "POST"])
def patients():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age_text = request.form.get("age", "").strip()
        notes = request.form.get("notes", "").strip()
        try:
            age = int(age_text) if age_text else None
            if not name or (age is not None and not 0 <= age <= 130):
                raise ValueError
            with connect_db() as con:
                con.execute(
                    "INSERT INTO patients(name, age, notes, created_at) VALUES (?, ?, ?, ?)",
                    (name, age, notes, now_iso())
                )
            flash("Patient added successfully.", "success")
            return redirect(url_for("patients"))
        except ValueError:
            flash("Enter a patient name and a valid age (0–130).", "error")
    with connect_db() as con:
        rows = con.execute("SELECT * FROM patients ORDER BY id DESC").fetchall()
    return render_template("patients.html", patients=rows)


@app.route("/api/readings", methods=["POST"])
@require_device_key
def add_reading():
    data = request.get_json(silent=True) or {}
    try:
        patient_id = int(data["patient_id"])
        values = {}
        for key in ("heart_rate", "spo2", "temperature"):
            raw = data.get(key)
            values[key] = float(raw) if raw is not None else None
            if values[key] is not None and not 0 <= values[key] <= 300:
                raise ValueError(f"Invalid {key} value")
        if all(v is None for v in values.values()):
            raise ValueError("At least one sensor value is required")
    except (KeyError, TypeError, ValueError) as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    timestamp = now_iso()
    with connect_db() as con:
        if not con.execute("SELECT id FROM patients WHERE id=?", (patient_id,)).fetchone():
            return jsonify({"ok": False, "error": "Patient not found"}), 404
        cur = con.execute(
            """INSERT INTO readings(patient_id, heart_rate, spo2, temperature, recorded_at)
               VALUES (?, ?, ?, ?, ?)""",
            (patient_id, values["heart_rate"], values["spo2"], values["temperature"], timestamp)
        )
        reading_id = cur.lastrowid
        messages = find_alerts(values)
        for message in messages:
            con.execute(
                "INSERT INTO alerts(patient_id, reading_id, message, created_at) VALUES (?, ?, ?, ?)",
                (patient_id, reading_id, message, timestamp)
            )
    return jsonify({"ok": True, "reading_id": reading_id, "alerts": messages}), 201


@app.route("/api/readings/latest")
def get_latest():
    patient_id = request.args.get("patient_id", type=int)
    if not patient_id:
        return jsonify({"ok": False, "error": "patient_id is required"}), 400
    with connect_db() as con:
        row = con.execute(
            "SELECT * FROM readings WHERE patient_id=? ORDER BY id DESC LIMIT 1", (patient_id,)
        ).fetchone()
    return jsonify(dict(row) if row else {})


@app.route("/api/demo-reading", methods=["POST"])
def demo_reading():
    # Demo-only form; add user authentication/CSRF protection before deployment.
    try:
        patient_id = int(request.form["patient_id"])
        values = {
            "heart_rate": float(request.form["heart_rate"]),
            "spo2": float(request.form["spo2"]),
            "temperature": float(request.form["temperature"]),
        }
        if not (0 <= values["heart_rate"] <= 300 and 0 <= values["spo2"] <= 100
                and 0 <= values["temperature"] <= 60):
            raise ValueError
    except (KeyError, ValueError):
        flash("Please enter valid demo readings.", "error")
        return redirect(url_for("dashboard"))
    timestamp = now_iso()
    with connect_db() as con:
        if not con.execute("SELECT id FROM patients WHERE id=?", (patient_id,)).fetchone():
            flash("Patient not found.", "error")
            return redirect(url_for("dashboard"))
        cur = con.execute(
            """INSERT INTO readings(patient_id, heart_rate, spo2, temperature, recorded_at)
               VALUES (?, ?, ?, ?, ?)""",
            (patient_id, values["heart_rate"], values["spo2"], values["temperature"], timestamp)
        )
        for message in find_alerts(values):
            con.execute(
                "INSERT INTO alerts(patient_id, reading_id, message, created_at) VALUES (?, ?, ?, ?)",
                (patient_id, cur.lastrowid, message, timestamp)
            )
    flash("Demo reading saved (not a clinical measurement).", "success")
    return redirect(url_for("dashboard", patient_id=patient_id))


@app.route("/health")
def health():
    return jsonify({"status": "ok", "time": now_iso()})


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
