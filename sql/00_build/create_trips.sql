-- GENERADO por scripts/build_db.py: no editar a mano.
-- Materializa los Parquet de yellow y green en una tabla unica con esquema normalizado.
-- Transformaciones: renombrado a esquema comun, TRY_CAST explicito de tipos,
-- columnas ausentes en un tipo/anio -> NULL, trazabilidad por archivo (source_*).
-- No se filtra ni se corrige ningun registro: la limpieza queda para el analisis.
-- Fuentes: {'yellow': ['/workspace/data/raw/yellow/*/*.parquet'], 'green': ['/workspace/data/raw/green/*/*.parquet']}

CREATE TABLE trips AS
SELECT
    'yellow' AS taxi_type,
    TRY_CAST("VendorID" AS INTEGER) AS vendor_id,
    TRY_CAST("tpep_pickup_datetime" AS TIMESTAMP) AS pickup_datetime,
    TRY_CAST("tpep_dropoff_datetime" AS TIMESTAMP) AS dropoff_datetime,
    TRY_CAST("passenger_count" AS INTEGER) AS passenger_count,
    TRY_CAST("trip_distance" AS DOUBLE) AS trip_distance,
    TRY_CAST("RatecodeID" AS INTEGER) AS ratecode_id,
    TRY_CAST("store_and_fwd_flag" AS VARCHAR) AS store_and_fwd_flag,
    TRY_CAST("PULocationID" AS INTEGER) AS pu_location_id,
    TRY_CAST("DOLocationID" AS INTEGER) AS do_location_id,
    TRY_CAST("payment_type" AS INTEGER) AS payment_type,
    CAST(NULL AS INTEGER) AS trip_type,
    TRY_CAST("fare_amount" AS DOUBLE) AS fare_amount,
    TRY_CAST("extra" AS DOUBLE) AS extra,
    TRY_CAST("mta_tax" AS DOUBLE) AS mta_tax,
    TRY_CAST("tip_amount" AS DOUBLE) AS tip_amount,
    TRY_CAST("tolls_amount" AS DOUBLE) AS tolls_amount,
    CAST(NULL AS DOUBLE) AS ehail_fee,
    TRY_CAST("improvement_surcharge" AS DOUBLE) AS improvement_surcharge,
    TRY_CAST("congestion_surcharge" AS DOUBLE) AS congestion_surcharge,
    TRY_CAST("Airport_fee" AS DOUBLE) AS airport_fee,
    TRY_CAST("cbd_congestion_fee" AS DOUBLE) AS cbd_congestion_fee,
    TRY_CAST("total_amount" AS DOUBLE) AS total_amount,
    regexp_extract(filename, '[^/\\]+$') AS source_file,
    CAST(regexp_extract(filename, '(\d{4})-\d{2}\.parquet$', 1) AS SMALLINT) AS source_year,
    CAST(regexp_extract(filename, '\d{4}-(\d{2})\.parquet$', 1) AS SMALLINT) AS source_month
FROM read_parquet(['/workspace/data/raw/yellow/*/*.parquet'], union_by_name=true, filename=true)
UNION ALL
SELECT
    'green' AS taxi_type,
    TRY_CAST("VendorID" AS INTEGER) AS vendor_id,
    TRY_CAST("lpep_pickup_datetime" AS TIMESTAMP) AS pickup_datetime,
    TRY_CAST("lpep_dropoff_datetime" AS TIMESTAMP) AS dropoff_datetime,
    TRY_CAST("passenger_count" AS INTEGER) AS passenger_count,
    TRY_CAST("trip_distance" AS DOUBLE) AS trip_distance,
    TRY_CAST("RatecodeID" AS INTEGER) AS ratecode_id,
    TRY_CAST("store_and_fwd_flag" AS VARCHAR) AS store_and_fwd_flag,
    TRY_CAST("PULocationID" AS INTEGER) AS pu_location_id,
    TRY_CAST("DOLocationID" AS INTEGER) AS do_location_id,
    TRY_CAST("payment_type" AS INTEGER) AS payment_type,
    TRY_CAST("trip_type" AS INTEGER) AS trip_type,
    TRY_CAST("fare_amount" AS DOUBLE) AS fare_amount,
    TRY_CAST("extra" AS DOUBLE) AS extra,
    TRY_CAST("mta_tax" AS DOUBLE) AS mta_tax,
    TRY_CAST("tip_amount" AS DOUBLE) AS tip_amount,
    TRY_CAST("tolls_amount" AS DOUBLE) AS tolls_amount,
    TRY_CAST("ehail_fee" AS DOUBLE) AS ehail_fee,
    TRY_CAST("improvement_surcharge" AS DOUBLE) AS improvement_surcharge,
    TRY_CAST("congestion_surcharge" AS DOUBLE) AS congestion_surcharge,
    CAST(NULL AS DOUBLE) AS airport_fee,
    TRY_CAST("cbd_congestion_fee" AS DOUBLE) AS cbd_congestion_fee,
    TRY_CAST("total_amount" AS DOUBLE) AS total_amount,
    regexp_extract(filename, '[^/\\]+$') AS source_file,
    CAST(regexp_extract(filename, '(\d{4})-\d{2}\.parquet$', 1) AS SMALLINT) AS source_year,
    CAST(regexp_extract(filename, '\d{4}-(\d{2})\.parquet$', 1) AS SMALLINT) AS source_month
FROM read_parquet(['/workspace/data/raw/green/*/*.parquet'], union_by_name=true, filename=true);
