-- geo_profiling.sql
-- Identify missing or malformed address components in address_table

-- 1. Count total rows
SELECT COUNT(*) AS total_addresses
FROM address_table;

-- 2. Count missing street, city, postcode, country
SELECT
  SUM(CASE WHEN street IS NULL OR TRIM(street) = '' THEN 1 ELSE 0 END) AS missing_street,
  SUM(CASE WHEN city IS NULL OR TRIM(city) = '' THEN 1 ELSE 0 END)   AS missing_city,
  SUM(CASE WHEN postcode IS NULL OR TRIM(postcode) = '' THEN 1 ELSE 0 END) AS missing_postcode,
  SUM(CASE WHEN country IS NULL OR TRIM(country) = '' THEN 1 ELSE 0 END)  AS missing_country
FROM address_table;

-- 3. Sample of malformed postcodes (non-numeric or wrong length)
SELECT postcode, COUNT(*) AS count
FROM address_table
WHERE postcode !~ '^[0-9]{4,10}$'
GROUP BY postcode
ORDER BY count DESC
LIMIT 20;
