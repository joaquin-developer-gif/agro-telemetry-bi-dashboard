import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MACHINES_FILE = BASE_DIR / "data" / "raw" / "machines.csv"
OUTPUT_FILE = BASE_DIR / "data" / "raw" / "telemetry_events.csv"

random.seed(42)

MODEL_CONFIG = {
    "M001": {
        "min_hours": 4.0,
        "max_hours": 8.0,
        "fuel_per_hour_min": 6.0,
        "fuel_per_hour_max": 9.0,
        "base_temp": 82,
    },
    "M002": {
        "min_hours": 3.0,
        "max_hours": 7.0,
        "fuel_per_hour_min": 4.0,
        "fuel_per_hour_max": 7.0,
        "base_temp": 78,
    },
    "M003": {
        "min_hours": 5.0,
        "max_hours": 10.0,
        "fuel_per_hour_min": 10.0,
        "fuel_per_hour_max": 16.0,
        "base_temp": 86,
    },
}


def read_machines():
    machines = []

    with open(MACHINES_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            machines.append(row)

    return machines


def calculate_alert(engine_temp, gps_signal, fuel_per_hour):
    if engine_temp >= 97:
        return "HIGH_TEMP", "HIGH"

    if gps_signal == "LOW_SIGNAL":
        return "GPS_SIGNAL", "MEDIUM"

    if fuel_per_hour >= 14:
        return "HIGH_FUEL_CONSUMPTION", "MEDIUM"

    return "", "LOW"


def generate_events():
    machines = read_machines()
    events = []

    start_date = datetime(2026, 6, 1, 8, 0, 0)
    event_id = 1

    for day in range(30):
        current_date = start_date + timedelta(days=day)

        for machine in machines:
            model_id = machine["model_id"]
            config = MODEL_CONFIG[model_id]

            event_hour = random.randint(7, 18)
            event_minute = random.choice([0, 15, 30, 45])
            event_time = current_date.replace(hour=event_hour, minute=event_minute)

            hours_worked = round(
                random.uniform(config["min_hours"], config["max_hours"]),
                2
            )

            fuel_per_hour = random.uniform(
                config["fuel_per_hour_min"],
                config["fuel_per_hour_max"]
            )

            fuel_used = round(hours_worked * fuel_per_hour, 2)

            engine_temp = round(
                random.normalvariate(config["base_temp"], 6),
                2
            )

            gps_signal = "LOW_SIGNAL" if random.random() < 0.08 else "OK"

            alert_code, severity = calculate_alert(
                engine_temp,
                gps_signal,
                fuel_per_hour
            )

            events.append({
                "event_id": event_id,
                "machine_id": machine["machine_id"],
                "event_time": event_time.strftime("%Y-%m-%d %H:%M:%S"),
                "hours_worked": hours_worked,
                "fuel_used_liters": fuel_used,
                "engine_temp": engine_temp,
                "gps_signal": gps_signal,
                "alert_code": alert_code,
                "severity": severity,
            })

            event_id += 1

    return events


def save_events(events):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, mode="w", encoding="utf-8", newline="") as file:
        fieldnames = [
            "event_id",
            "machine_id",
            "event_time",
            "hours_worked",
            "fuel_used_liters",
            "engine_temp",
            "gps_signal",
            "alert_code",
            "severity",
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(events)


if __name__ == "__main__":
    generated_events = generate_events()
    save_events(generated_events)

    print(f"Telemetría generada correctamente: {OUTPUT_FILE}")
    print(f"Total de eventos generados: {len(generated_events)}")