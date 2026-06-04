import csv
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "db" / "agro_telemetry.db"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

EXPORTS = {
    "vw_dealer_summary": "dealer_summary.csv",
    "vw_zone_summary": "zone_summary.csv",
    "vw_machine_summary": "machine_summary.csv",
    "vw_daily_metrics": "daily_metrics.csv",
}


def export_view(connection, view_name, output_file):
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(f"SELECT * FROM {view_name}")
    rows = cursor.fetchall()

    if not rows:
        print(f"No hay datos para exportar desde {view_name}")
        return

    columns = rows[0].keys()

    with open(output_file, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()

        for row in rows:
            writer.writerow(dict(row))

    print(f"Exportado: {view_name} → {output_file}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_FILE)

    try:
        for view_name, filename in EXPORTS.items():
            output_file = OUTPUT_DIR / filename
            export_view(connection, view_name, output_file)

        print("")
        print("Archivos CSV para dashboard generados correctamente.")

    except Exception as error:
        print("Error exportando CSV:")
        print(error)

    finally:
        connection.close()


if __name__ == "__main__":
    main()