-- Objetivo: 3.6 perfil estadistico de cada columna de green (minimo, maximo, cuartiles, % de nulos): permite ver valores imposibles.
-- Fuente: /workspace/data/raw/green/*/*.parquet
SUMMARIZE SELECT * FROM read_parquet('/workspace/data/raw/green/*/*.parquet', union_by_name = true);
