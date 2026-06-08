-- =========================================================
-- Agro Telemetry BI Dashboard - AWS Athena Business Queries
-- Stage 3: AWS Data Lake with S3, Glue and Athena
-- Database: agro_telemetry_db
-- Main table: daily_metrics
-- =========================================================


-- =========================================================
-- 1. General executive KPIs
-- =========================================================
SELECT
    COUNT(DISTINCT machine_id) AS total_machines,
    ROUND(SUM(daily_hours_worked), 2) AS total_hours_worked,
    ROUND(SUM(daily_fuel_used), 2) AS total_fuel_used,
    SUM(daily_alerts) AS total_alerts,
    ROUND(AVG(avg_engine_temp), 2) AS avg_engine_temp
FROM agro_telemetry_db.daily_metrics;


-- =========================================================
-- 2. Operational summary by zone
-- =========================================================
SELECT 
    zona,
    ROUND(SUM(daily_fuel_used), 2) AS total_fuel_used,
    ROUND(SUM(daily_hours_worked), 2) AS total_hours_worked,
    SUM(daily_alerts) AS total_alerts,
    ROUND(AVG(avg_engine_temp), 2) AS avg_engine_temp
FROM agro_telemetry_db.daily_metrics
GROUP BY zona
ORDER BY total_fuel_used DESC;


-- =========================================================
-- 3. Operational summary by dealer
-- =========================================================
SELECT 
    concesionario,
    zona,
    ROUND(SUM(daily_fuel_used), 2) AS total_fuel_used,
    ROUND(SUM(daily_hours_worked), 2) AS total_hours_worked,
    SUM(daily_alerts) AS total_alerts,
    ROUND(AVG(avg_engine_temp), 2) AS avg_engine_temp
FROM agro_telemetry_db.daily_metrics
GROUP BY concesionario, zona
ORDER BY total_alerts DESC, total_fuel_used DESC;


-- =========================================================
-- 4. Machines with highest alerts and fuel consumption
-- =========================================================
SELECT
    machine_id,
    modelo,
    zona,
    concesionario,
    ROUND(SUM(daily_hours_worked), 2) AS total_hours_worked,
    ROUND(SUM(daily_fuel_used), 2) AS total_fuel_used,
    SUM(daily_alerts) AS total_alerts,
    ROUND(AVG(avg_engine_temp), 2) AS avg_engine_temp
FROM agro_telemetry_db.daily_metrics
GROUP BY machine_id, modelo, zona, concesionario
ORDER BY total_alerts DESC, total_fuel_used DESC;


-- =========================================================
-- 5. Daily operational evolution
-- =========================================================
SELECT
    event_date,
    ROUND(SUM(daily_hours_worked), 2) AS total_hours_worked,
    ROUND(SUM(daily_fuel_used), 2) AS total_fuel_used,
    SUM(daily_alerts) AS total_alerts,
    ROUND(AVG(avg_engine_temp), 2) AS avg_engine_temp
FROM agro_telemetry_db.daily_metrics
GROUP BY event_date
ORDER BY event_date;


-- =========================================================
-- 6. Fuel efficiency by machine model
-- =========================================================
SELECT
    modelo,
    COUNT(DISTINCT machine_id) AS total_machines,
    ROUND(SUM(daily_hours_worked), 2) AS total_hours_worked,
    ROUND(SUM(daily_fuel_used), 2) AS total_fuel_used,
    ROUND(SUM(daily_fuel_used) / NULLIF(SUM(daily_hours_worked), 0), 2) AS fuel_per_hour,
    SUM(daily_alerts) AS total_alerts,
    ROUND(AVG(avg_engine_temp), 2) AS avg_engine_temp
FROM agro_telemetry_db.daily_metrics
GROUP BY modelo
ORDER BY fuel_per_hour DESC;


-- =========================================================
-- 7. High temperature monitoring
-- =========================================================
SELECT
    event_date,
    machine_id,
    modelo,
    zona,
    concesionario,
    daily_hours_worked,
    daily_fuel_used,
    daily_alerts,
    avg_engine_temp
FROM agro_telemetry_db.daily_metrics
WHERE avg_engine_temp >= 85
ORDER BY avg_engine_temp DESC, daily_alerts DESC;

