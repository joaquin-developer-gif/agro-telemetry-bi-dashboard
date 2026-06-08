## Etapa 3 - AWS Data Lake con S3, Glue y Athena

En esta etapa se implementó una arquitectura básica de Data Lake en AWS para consultar datos de telemetría agrícola usando servicios cloud.

### Servicios utilizados

- Amazon S3: almacenamiento de archivos CSV crudos y procesados.
- AWS Glue Crawler: detección automática de esquemas.
- AWS Glue Data Catalog: catálogo de tablas.
- Amazon Athena: consultas SQL serverless sobre datos almacenados en S3.

### Bucket S3

Bucket utilizado:

```text
agro-telemetry-bi-dashboard-joaquin-2026
