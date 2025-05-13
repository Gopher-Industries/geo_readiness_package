# geo_geocode.py
# Read cleaned addresses from DB, call Google Maps Geocoding API, write back lat/lng/status.

import os
import time
import psycopg2
from googlemaps import Client as GoogleMaps

DB_DSN   = os.getenv('DATABASE_URL')         # e.g. postgres://user:pass@host/db
API_KEY  = os.getenv('GOOGLE_MAPS_API_KEY')
BATCH_SZ = 100

def get_conn():
    return psycopg2.connect(DB_DSN)

def fetch_pending(cur, batch_size):
    cur.execute("""
        SELECT id,
               street || ', ' || city || ', ' || postcode || ', ' || country AS full_addr
        FROM address_table
        WHERE (latitude IS NULL OR longitude IS NULL)
          AND geo_status IS DISTINCT FROM 'IN_PROGRESS'
        LIMIT %s
    """, (batch_size,))
    return cur.fetchall()

def geocode_and_update():
    gmaps = GoogleMaps(API_KEY)
    conn  = get_conn()
    cur   = conn.cursor()

    rows = fetch_pending(cur, BATCH_SZ)
    for rec_id, addr in rows:
        cur.execute("UPDATE address_table SET geo_status = 'IN_PROGRESS' WHERE id=%s", (rec_id,))
        conn.commit()
        try:
            res = gmaps.geocode(addr)
            if res:
                lat = res[0]['geometry']['location']['lat']
                lng = res[0]['geometry']['location']['lng']
                status = 'OK'
            else:
                lat = None
                lng = None
                status = 'NOT_FOUND'
        except Exception:
            lat, lng, status = None, None, 'ERROR'
        cur.execute("""
            UPDATE address_table
            SET latitude=%s, longitude=%s, geo_status=%s, updated_at=NOW()
            WHERE id=%s
        """, (lat, lng, status, rec_id))
        conn.commit()
        time.sleep(0.1)  # rate-limit
    cur.close()
    conn.close()

if __name__ == "__main__":
    geocode_and_update()
