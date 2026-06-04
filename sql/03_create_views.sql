DROP VIEW IF EXISTS vw_dealer_summary;
DROP VIEW IF EXISTS vw_zone_summary;
DROP VIEW IF EXISTS vw_machine_summary;
DROP VIEW IF EXISTS vw_daily_metrics;

-- =====================================================
-- Vista 1: resumen por concesionario
-- =====================================================

CREATE VIEW vw_dealer_summary AS
SELECT
    d.dealer_id,
    d.concesionario,
    d.zona,
    d.provincia,
    d.ciudad,
    COUNT(DISTINCT m.machine_id) AS total_machines,
    ROUND(SUM(t.hours_worked), 2) AS total_hours_worked,
    ROUND(SUM(t.fuel_used_liters), 2) AS total_fuel_used,
    COUNT(
        CASE 
            WHEN t.alert_code IS NOT NULL AND t.alert_code <> '' 
            THEN 1 
        END
    ) AS total_alerts,
    ROUND(AVG(t.engine_temp), 2) AS avg_engine_temp,
    ROUND(
        SUM(t.hours_worked) * 0.4 +
        SUM(t.fuel_used_liters) * 0.3 +
        COUNT(
            CASE 
                WHEN t.alert_code IS NOT NULL AND t.alert_code <> '' 
                THEN 1 
            END
        ) * 10,
        2
    ) AS operational_score
FROM telemetry_events t
JOIN machines m ON t.machine_id = m.machine_id
JOIN dealers d ON m.dealer_id = d.dealer_id
GROUP BY
    d.dealer_id,
    d.concesionario,
    d.zona,
    d.provincia,
    d.ciudad;


-- =====================================================
-- Vista 2: resumen por zona
-- =====================================================

CREATE VIEW vw_zone_summary AS
SELECT
    d.zona,
    COUNT(DISTINCT d.dealer_id) AS total_dealers,
    COUNT(DISTINCT m.machine_id) AS total_machines,
    ROUND(SUM(t.hours_worked), 2) AS total_hours_worked,
    ROUND(SUM(t.fuel_used_liters), 2) AS total_fuel_used,
    COUNT(
        CASE 
            WHEN t.alert_code IS NOT NULL AND t.alert_code <> '' 
            THEN 1 
        END
    ) AS total_alerts,
    ROUND(AVG(t.engine_temp), 2) AS avg_engine_temp
FROM telemetry_events t
JOIN machines m ON t.machine_id = m.machine_id
JOIN dealers d ON m.dealer_id = d.dealer_id
GROUP BY d.zona;


-- =====================================================
-- Vista 3: resumen por máquina
-- =====================================================

CREATE VIEW vw_machine_summary AS
SELECT
    m.machine_id,
    mm.modelo,
    mm.marca,
    mm.potencia_hp,
    mm.cilindrada_litros,
    d.concesionario,
    d.zona,
    d.provincia,
    ROUND(SUM(t.hours_worked), 2) AS total_hours_worked,
    ROUND(SUM(t.fuel_used_liters), 2) AS total_fuel_used,
    COUNT(
        CASE 
            WHEN t.alert_code IS NOT NULL AND t.alert_code <> '' 
            THEN 1 
        END
    ) AS total_alerts,
    ROUND(AVG(t.engine_temp), 2) AS avg_engine_temp
FROM telemetry_events t
JOIN machines m ON t.machine_id = m.machine_id
JOIN machine_models mm ON m.model_id = mm.model_id
JOIN dealers d ON m.dealer_id = d.dealer_id
GROUP BY
    m.machine_id,
    mm.modelo,
    mm.marca,
    mm.potencia_hp,
    mm.cilindrada_litros,
    d.concesionario,
    d.zona,
    d.provincia;


-- =====================================================
-- Vista 4: métricas diarias
-- =====================================================

CREATE VIEW vw_daily_metrics AS
SELECT
    DATE(t.event_time) AS event_date,
    d.zona,
    d.concesionario,
    m.machine_id,
    mm.modelo,
    ROUND(SUM(t.hours_worked), 2) AS daily_hours_worked,
    ROUND(SUM(t.fuel_used_liters), 2) AS daily_fuel_used,
    COUNT(
        CASE 
            WHEN t.alert_code IS NOT NULL AND t.alert_code <> '' 
            THEN 1 
        END
    ) AS daily_alerts,
    ROUND(AVG(t.engine_temp), 2) AS avg_engine_temp
FROM telemetry_events t
JOIN machines m ON t.machine_id = m.machine_id
JOIN machine_models mm ON m.model_id = mm.model_id
JOIN dealers d ON m.dealer_id = d.dealer_id
GROUP BY
    DATE(t.event_time),
    d.zona,
    d.concesionario,
    m.machine_id,
    mm.modelo;