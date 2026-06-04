import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "db" / "agro_telemetry.db"
VIEWS_FILE = BASE_DIR / "sql" / "03_create_views.sql"


def main():
    connection = sqlite3.connect(DB_FILE)

    try:
        with open(VIEWS_FILE, mode="r", encoding="utf-8") as file:
            views_sql = file.read()

        connection.executescript(views_sql)
        connection.commit()

        print("Vistas creadas correctamente:")
        print("- vw_dealer_summary")
        print("- vw_zone_summary")
        print("- vw_machine_summary")
        print("- vw_daily_metrics")

    except Exception as error:
        connection.rollback()
        print("Error creando vistas:")
        print(error)

    finally:
        connection.close()


if __name__ == "__main__":
    main()
