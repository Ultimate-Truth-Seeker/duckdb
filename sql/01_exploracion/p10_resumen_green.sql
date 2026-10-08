-- Objetivo: 3.6 perfil estadistico de cada columna de green (minimo, maximo, cuartiles, % de nulos): permite ver valores imposibles.
-- Fuente: /workspace/data/raw/green/*/*.parquet
-- Decision: green tambien tiene distancias y tarifas extremas. ehail_fee es 100 % nulo, no se usa en ningun indicador.
SUMMARIZE SELECT * FROM read_parquet('/workspace/data/raw/green/*/*.parquet', union_by_name = true);
