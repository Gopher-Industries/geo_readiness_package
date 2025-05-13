-- GeoReadinessCheck.sql
-- A Postgres stored procedure to run the full pipeline in-db

CREATE OR REPLACE FUNCTION dbo.GeoReadinessCheck()
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
  -- 1. Mark any new rows as PENDING
  UPDATE address_table
  SET geo_status = 'PENDING'
  WHERE (latitude IS NULL OR longitude IS NULL)
    AND (geo_status IS NULL OR geo_status <> 'IN_PROGRESS');

  -- 2. Call out to our Python script via an external job / dblink
  --    (Assumes you have a trigger in your job agent to run geo_geocode.py)

  -- 3. Flag failures to a side table
  INSERT INTO geo_exceptions (address_id, street, city, postcode, reason, occurred_at)
  SELECT a.id, a.street, a.city, a.postcode,
         COALESCE(a.geo_status, 'UNKNOWN') AS reason,
         NOW()
  FROM address_table a
  WHERE a.geo_status <> 'OK';

  -- 4. Optionally, generate a quick summary table
  INSERT INTO geo_summary (snapshot_time, total, success, failures)
  SELECT NOW(),
         COUNT(*),
         COUNT(*) FILTER (WHERE geo_status = 'OK'),
         COUNT(*) FILTER (WHERE geo_status <> 'OK')
  FROM address_table;
END;
$$;
