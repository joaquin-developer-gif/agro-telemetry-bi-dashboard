import csv
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "db" / "agro_telemetry.db"

SQL_SCHEMA_FILE = BASE_DIR / "sql" / "01_create_tables.sql"

MACHINE_MODELS_FILE = BASE_DIR / "data" / "raw" / "machine_models.csv"
DEALERS_FILE = BASE_DIR / "data" / "raw" / "dealers.csv"
MACHINES_FILE = BASE_DIR / "data" / "raw" / "machines.csv"
TELEMETRY_FILE = BASE_DIR / "data" / "raw" / "telemetry_events.csv"


def execute_schema(connection):
    with open(SQL_SCHEMA_FILE, mode="r", encoding="utf-8") as file:
        schema_sql = file.read()

    connection.executescript(schema_sql)


def load_csv(connection, table_name, csv_file):
    with open(csv_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    if not rows:
        print(f"No hay datos para cargar en {table_name}")
        return

    columns = rows[0].keys()
    columns_sql = ", ".join(columns)
    placeholders = ", ".join(["?"] * len(columns))

    query = f"""
    INSERT INTO {table_name} ({columns_sql})
    VALUES ({placeholders})
    """

    values = [
        [row[column] for column in columns]
        for row in rows
    ]

    connection.executemany(query, values)
    print(f"Tabla cargada: {table_name} | Registros: {len(rows)}")


def main():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_FILE)

    try:
        execute_schema(connection)

        load_csv(connection, "machine_models", MACHINE_MODELS_FILE)
        load_csv(connection, "dealers", DEALERS_FILE)
        load_csv(connection, "machines", MACHINES_FILE)
        load_csv(connection, "telemetry_events", TELEMETRY_FILE)

        connection.commit()

        print("")
        print("Base de datos creada correctamente.")
        print(f"Archivo SQLite: {DB_FILE}")

    except Exception as error:
        connection.rollback()
        print("Error cargando datos:")
        print(error)

    finally:
        connection.close()


if __name__ == "__main__":
    main()