-- Objetivo: 3.6 perfil estadistico de cada columna de yellow (minimo, maximo, cuartiles, % de nulos): permite ver valores imposibles.
-- Fuente: /workspace/data/raw/yellow/*/*.parquet
SUMMARIZE SELECT * FROM read_parquet('/workspace/data/raw/yellow/*/*.parquet', union_by_name = true);
