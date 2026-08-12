"""
Extraction multi-sources vers l'entrepôt DuckDB (schéma `raw`).
Trois sources hétérogènes :
  1. BASE DE DONNÉES : ventes depuis PostgreSQL (extension DuckDB `postgres`)
  2. GÉNÉRÉE       : table calendrier
  3. API REST      : météo quotidienne (Open-Meteo, sans clé)
"""
import json
import urllib.request
from datetime import date, timedelta
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "warehouse" / "warehouse.duckdb"
PG = "host=127.0.0.1 port=5433 dbname=ecommerce user=portfolio password=portfolio"
START, END = "2024-08-01", "2026-08-31"
# L'archive météo ne couvre pas le futur (ni les ~5 derniers jours) : on plafonne.
WEATHER_END = min(END, (date.today() - timedelta(days=7)).isoformat())
LAT, LON = 48.85, 2.35   # Paris (météo de référence)


def fetch_weather() -> list[tuple]:
    url = (f"https://archive-api.open-meteo.com/v1/archive?latitude={LAT}&longitude={LON}"
           f"&start_date={START}&end_date={WEATHER_END}"
           f"&daily=temperature_2m_mean,precipitation_sum&timezone=Europe%2FParis")
    with urllib.request.urlopen(url, timeout=60) as r:
        d = json.load(r)["daily"]
    return list(zip(d["time"], d["temperature_2m_mean"], d["precipitation_sum"]))


def main() -> None:
    DB.parent.mkdir(exist_ok=True)
    con = duckdb.connect(str(DB))
    con.execute("CREATE SCHEMA IF NOT EXISTS raw;")

    # 1. Source BASE DE DONNÉES — ventes depuis PostgreSQL
    con.execute("INSTALL postgres; LOAD postgres;")
    con.execute(f"ATTACH '{PG}' AS pg (TYPE postgres, READ_ONLY);")
    for t in ["orders", "order_item", "customer", "product", "category"]:
        con.execute(f"CREATE OR REPLACE TABLE raw.{t} AS SELECT * FROM pg.public.{t};")
    con.execute("DETACH pg;")

    # 2. Source GÉNÉRÉE — calendrier
    con.execute(f"""
        CREATE OR REPLACE TABLE raw.calendar AS
        SELECT unnest(generate_series(DATE '{START}', DATE '{END}', INTERVAL '1 day'))::date AS date;
    """)

    # 3. Source API — météo quotidienne
    con.execute("CREATE OR REPLACE TABLE raw.weather (date DATE, temp_mean DOUBLE, precip DOUBLE);")
    con.executemany("INSERT INTO raw.weather VALUES (?, ?, ?)", fetch_weather())

    print("Extraction -> warehouse.duckdb (schéma raw) :")
    for t in ["orders", "order_item", "customer", "product", "category", "calendar", "weather"]:
        n = con.execute(f"SELECT count(*) FROM raw.{t}").fetchone()[0]
        print(f"  raw.{t}: {n}")
    con.close()


if __name__ == "__main__":
    main()
