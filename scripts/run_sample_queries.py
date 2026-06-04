import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "db" / "agro_telemetry.db"


def print_results(title, query):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    print("")
    print("=" * 80)
    print(title)
    print("=" * 80)

    cursor.execute(query)

    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()

    print(" | ".join(columns))
    print("-" * 80)

    for row in rows:
        print(" | ".join(str(value) for value in row))

    connection.close()


if __name__ == "__main__":
    print_results(
        "Ranking completo por concesionario",
        """
        SELECT
            d.dealer_id,
            d.concesionario,
            d.zona,
            COUNT(DISTINCT m.machine_id) AS total_machines,
            ROUND(SUM(t.hours_worked), 2) AS total_hours_worked,
            ROUND(SUM(t.fuel_used_liters), 2) AS total_fuel_used,
            COUNT(CASE WHEN t.alert_code IS NOT NULL AND t.alert_code <> '' THEN 1 END) AS total_alerts,
            ROUND(AVG(t.engine_temp), 2) AS avg_engine_temp
        FROM telemetry_events t
        JOIN machines m ON t.machine_id = m.machine_id
        JOIN dealers d ON m.dealer_id = d.dealer_id
        GROUP BY d.dealer_id, d.concesionario, d.zona
        ORDER BY total_alerts DESC, total_fuel_used DESC;
        """
    )

    print_results(
        "Consumo total por zona",
        """
        SELECT
            d.zona,
            ROUND(SUM(t.fuel_used_liters), 2) AS total_fuel_used
        FROM telemetry_events t
        JOIN machines m ON t.machine_id = m.machine_id
        JOIN dealers d ON m.dealer_id = d.dealer_id
        GROUP BY d.zona
        ORDER BY total_fuel_used DESC;
        """
    )

    print_results(
        "Alertas por concesionario",
        """
        SELECT
            d.concesionario,
            d.zona,
            COUNT(*) AS total_alerts
        FROM telemetry_events t
        JOIN machines m ON t.machine_id = m.machine_id
        JOIN dealers d ON m.dealer_id = d.dealer_id
        WHERE t.alert_code IS NOT NULL
          AND t.alert_code <> ''
        GROUP BY d.concesionario, d.zona
        ORDER BY total_alerts DESC;
        """
    )