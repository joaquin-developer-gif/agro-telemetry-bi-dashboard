DROP TABLE IF EXISTS telemetry_events;
DROP TABLE IF EXISTS machines;
DROP TABLE IF EXISTS dealers;
DROP TABLE IF EXISTS machine_models;

CREATE TABLE machine_models (
    model_id TEXT PRIMARY KEY,
    modelo TEXT NOT NULL,
    marca TEXT NOT NULL,
    potencia_hp INTEGER NOT NULL,
    cilindrada_litros REAL NOT NULL,
    cilindrada_cm3 INTEGER NOT NULL
);

CREATE TABLE dealers (
    dealer_id TEXT PRIMARY KEY,
    concesionario TEXT NOT NULL,
    zona TEXT NOT NULL,
    provincia TEXT NOT NULL,
    ciudad TEXT NOT NULL
);

CREATE TABLE machines (
    machine_id TEXT PRIMARY KEY,
    model_id TEXT NOT NULL,
    dealer_id TEXT NOT NULL,
    estado TEXT NOT NULL,
    FOREIGN KEY (model_id) REFERENCES machine_models(model_id),
    FOREIGN KEY (dealer_id) REFERENCES dealers(dealer_id)
);

CREATE TABLE telemetry_events (
    event_id INTEGER PRIMARY KEY,
    machine_id TEXT NOT NULL,
    event_time TEXT NOT NULL,
    hours_worked REAL NOT NULL,
    fuel_used_liters REAL NOT NULL,
    engine_temp REAL NOT NULL,
    gps_signal TEXT NOT NULL,
    alert_code TEXT,
    severity TEXT NOT NULL,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
);