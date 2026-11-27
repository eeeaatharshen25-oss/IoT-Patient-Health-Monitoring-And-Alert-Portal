# IoT Patient Health Monitoring and Alert Portal

A full-stack educational starter project with a responsive frontend, Flask backend, SQLite database, patient records, sensor-reading API, and alert history.

## Stack
- Frontend: HTML, CSS, JavaScript
- Backend: Python + Flask
- Database: SQLite (created automatically)
- IoT device: ESP32 over Wi-Fi using HTTP POST

## Run locally
1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Create an environment and install dependencies:
   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\activate
   # macOS/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env`, then change `SECRET_KEY` and `API_KEY`.
5. Start:
   ```bash
   python app.py
   ```
6. Visit http://127.0.0.1:5000

A demo patient is created automatically. Use the dashboard's manual demo form to test the UI before connecting hardware.

## API for ESP32
`POST /api/readings` with headers `Content-Type: application/json` and `X-API-Key: <your API_KEY>`.

Example JSON:
```json
{"patient_id": 1, "heart_rate": 76, "spo2": 98, "temperature": 36.8}
```

`GET /api/readings/latest?patient_id=1` returns the latest saved reading.

## ESP32
See `hardware/esp32_patient_monitor.ino`. Install the SparkFun MAX3010x library in Arduino IDE and set Wi-Fi, server URL, patient ID, and API key in the sketch. The sample sketch sends pulse-oximeter values as a prototype; sensor algorithms and hardware readings require validation. Temperature is left as a placeholder until a compatible sensor is wired.

## GitHub
Do not upload `.env`, database files, real patient data, Wi-Fi passwords, or API keys. `.gitignore` excludes them.

## Safety
This is an educational prototype, not a certified medical device. Demo thresholds are not clinical guidance. Do not use it for diagnosis, treatment decisions, or emergency monitoring. Real deployment requires clinical validation, security review, privacy controls, HTTPS, authentication/authorization, audit logging, and reliable alert delivery.
