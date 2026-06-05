# Etapa 3 - AWS Data Lake

Esta etapa implementa una arquitectura cloud básica para el proyecto Agro Telemetry BI Dashboard utilizando servicios de AWS.

## Objetivo

Llevar los archivos CSV generados por el pipeline local hacia una arquitectura cloud de análisis de datos.

## Servicios utilizados

- Amazon S3
- AWS Glue Data Catalog
- AWS Glue Crawler
- Amazon Athena

## Flujo de datos

```text
CSV locales
    ↓
Amazon S3
    ↓
AWS Glue Crawler
    ↓
AWS Glue Data Catalog
    ↓
Amazon Athena
    ↓
Consultas SQL analíticas