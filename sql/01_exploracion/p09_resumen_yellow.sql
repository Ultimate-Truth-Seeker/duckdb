-- Objetivo: 3.6 perfil estadistico de cada columna de yellow (minimo, maximo, cuartiles, % de nulos): permite ver valores imposibles.
-- Fuente: /workspace/data/raw/yellow/*/*.parquet
-- Decision: yellow: trip_distance llega a 398,608 millas y fare_amount a 863,372 (y minimo -2,555): hay valores imposibles. passenger_count, RatecodeID y store_and_fwd_flag tienen 19.6 % de nulos. las fechas van de 2001 a 2026.
SUMMARIZE SELECT * FROM read_parquet('/workspace/data/raw/yellow/*/*.parquet', union_by_name = true);
