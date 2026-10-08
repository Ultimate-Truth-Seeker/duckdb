-- Objetivo: 3.3 y 3.4 columnas y tipos de datos de los archivos de taxis amarillos (esquema unificado de todos los archivos).
-- Fuente: /workspace/data/raw/yellow/*/*.parquet
-- Decision: 21 columnas en yellow. nombres con mayusculas mezcladas (VendorID, Airport_fee) y prefijo tpep_; se normalizan a minusculas en taxi_common.py.
DESCRIBE SELECT * FROM read_parquet('/workspace/data/raw/yellow/*/*.parquet', union_by_name = true);
