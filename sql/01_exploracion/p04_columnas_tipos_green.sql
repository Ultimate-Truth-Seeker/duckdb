-- Objetivo: 3.3 y 3.4 columnas y tipos de datos de los archivos de taxis verdes (esquema unificado de todos los archivos).
-- Fuente: /workspace/data/raw/green/*/*.parquet
DESCRIBE SELECT * FROM read_parquet('/workspace/data/raw/green/*/*.parquet', union_by_name = true);
