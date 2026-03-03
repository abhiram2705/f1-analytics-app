"""
Export F1 analytics data from SQLite to CSV files for Power BI.
Run from the backend folder:
    python ../powerbi/export_csv.py

Outputs CSVs into ../powerbi/data/
"""
import sqlite3
import csv
import os
import sys

DB_PATH   = os.path.join(os.path.dirname(__file__), "..", "backend", "f1_analytics.db")
OUT_DIR   = os.path.join(os.path.dirname(__file__), "data")

os.makedirs(OUT_DIR, exist_ok=True)

QUERIES = {
    "fastest_laps": """
        SELECT
            r.season,
            r.round,
            r.name         AS race_name,
            r.date         AS race_date,
            ci.name        AS circuit,
            ci.country,
            d.code         AS driver_code,
            d.full_name    AS driver_name,
            d.team_id,
            co.name        AS team_name,
            l.lap_number,
            ROUND(l.lap_time_ms / 1000.0, 3)  AS lap_time_sec,
            ROUND(l.s1_ms / 1000.0, 3)        AS s1_sec,
            ROUND(l.s2_ms / 1000.0, 3)        AS s2_sec,
            ROUND(l.s3_ms / 1000.0, 3)        AS s3_sec,
            l.compound
        FROM laps l
        JOIN races r    ON r.race_id   = l.race_id
        JOIN drivers d  ON d.driver_id = l.driver_id
        LEFT JOIN circuits ci     ON ci.circuit_id = r.circuit_id
        LEFT JOIN constructors co ON co.team_id    = d.team_id
        WHERE l.lap_time_ms IS NOT NULL
          AND l.lap_time_ms = (
              SELECT MIN(l2.lap_time_ms)
              FROM laps l2
              WHERE l2.race_id   = l.race_id
                AND l2.driver_id = l.driver_id
                AND l2.lap_time_ms IS NOT NULL
          )
        ORDER BY r.season, r.round, l.lap_time_ms
    """,

    "tyre_degradation": """
        SELECT
            r.season,
            r.round,
            r.name         AS race_name,
            r.date         AS race_date,
            d.code         AS driver_code,
            d.full_name    AS driver_name,
            co.name        AS team_name,
            l.compound,
            l.tyre_life,
            ROUND(l.lap_time_ms / 1000.0, 3) AS lap_time_sec,
            l.lap_number
        FROM laps l
        JOIN races r    ON r.race_id   = l.race_id
        JOIN drivers d  ON d.driver_id = l.driver_id
        LEFT JOIN constructors co ON co.team_id = d.team_id
        WHERE l.lap_time_ms IS NOT NULL
          AND l.compound IS NOT NULL
          AND l.tyre_life IS NOT NULL
          AND (l.track_status = '1' OR l.track_status IS NULL)
        ORDER BY r.season, r.round, l.compound, l.tyre_life
    """,

    "pit_stops": """
        SELECT
            r.season,
            r.round,
            r.name          AS race_name,
            r.date          AS race_date,
            d.code          AS driver_code,
            d.full_name     AS driver_name,
            co.name         AS team_name,
            p.stop_number,
            p.lap,
            ROUND(p.duration_ms / 1000.0, 3) AS duration_sec
        FROM pit_stops p
        JOIN races r    ON r.race_id   = p.race_id
        JOIN drivers d  ON d.driver_id = p.driver_id
        LEFT JOIN constructors co ON co.team_id = d.team_id
        ORDER BY r.season, r.round, p.lap
    """,

    "stints": """
        SELECT
            r.season,
            r.round,
            r.name          AS race_name,
            r.date          AS race_date,
            d.code          AS driver_code,
            d.full_name     AS driver_name,
            co.name         AS team_name,
            s.stint_number,
            s.compound,
            s.start_lap,
            s.end_lap,
            (s.end_lap - s.start_lap + 1) AS stint_length
        FROM stints s
        JOIN races r    ON r.race_id   = s.race_id
        JOIN drivers d  ON d.driver_id = s.driver_id
        LEFT JOIN constructors co ON co.team_id = d.team_id
        ORDER BY r.season, r.round, d.code, s.stint_number
    """,

    "race_results": """
        SELECT
            r.season,
            r.round,
            r.name          AS race_name,
            r.date          AS race_date,
            ci.name         AS circuit,
            ci.country,
            d.code          AS driver_code,
            d.full_name     AS driver_name,
            co.name         AS team_name,
            rr.position,
            rr.grid,
            rr.points,
            rr.status
        FROM race_results rr
        JOIN races r    ON r.race_id   = rr.race_id
        JOIN drivers d  ON d.driver_id = rr.driver_id
        LEFT JOIN circuits ci     ON ci.circuit_id = r.circuit_id
        LEFT JOIN constructors co ON co.team_id    = d.team_id
        ORDER BY r.season, r.round, rr.position
    """,

    "driver_standings": """
        SELECT
            ds.season,
            ds.round,
            r.name          AS race_name,
            d.code          AS driver_code,
            d.full_name     AS driver_name,
            co.name         AS team_name,
            ds.position,
            ds.points,
            ds.wins
        FROM driver_standings ds
        JOIN drivers d  ON d.driver_id = ds.driver_id
        LEFT JOIN constructors co ON co.team_id = d.team_id
        LEFT JOIN races r ON r.season = ds.season AND r.round = ds.round
        ORDER BY ds.season, ds.round, ds.position
    """,

    "constructor_standings": """
        SELECT
            cs.season,
            cs.round,
            r.name          AS race_name,
            co.name         AS team_name,
            cs.position,
            cs.points,
            cs.wins
        FROM constructor_standings cs
        LEFT JOIN constructors co ON co.team_id = cs.team_id
        LEFT JOIN races r ON r.season = cs.season AND r.round = cs.round
        ORDER BY cs.season, cs.round, cs.position
    """,

    "all_laps": """
        SELECT
            r.season,
            r.round,
            r.name          AS race_name,
            d.code          AS driver_code,
            d.full_name     AS driver_name,
            co.name         AS team_name,
            l.lap_number,
            ROUND(l.lap_time_ms / 1000.0, 3)  AS lap_time_sec,
            ROUND(l.s1_ms / 1000.0, 3)        AS s1_sec,
            ROUND(l.s2_ms / 1000.0, 3)        AS s2_sec,
            ROUND(l.s3_ms / 1000.0, 3)        AS s3_sec,
            l.compound,
            l.tyre_life,
            l.is_personal_best,
            l.track_status
        FROM laps l
        JOIN races r    ON r.race_id   = l.race_id
        JOIN drivers d  ON d.driver_id = l.driver_id
        LEFT JOIN constructors co ON co.team_id = d.team_id
        WHERE l.lap_time_ms IS NOT NULL
        ORDER BY r.season, r.round, d.code, l.lap_number
    """,
}

def export_all():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: DB not found at {os.path.abspath(DB_PATH)}")
        sys.exit(1)

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    total_rows = 0
    for name, query in QUERIES.items():
        out_path = os.path.join(OUT_DIR, f"{name}.csv")
        cur.execute(query.strip())
        rows = cur.fetchall()
        if not rows:
            print(f"  {name}.csv  — 0 rows (no data yet)")
            continue
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows([dict(r) for r in rows])
        print(f"  {name}.csv  -- {len(rows):,} rows  ->  {out_path}")
        total_rows += len(rows)

    con.close()
    print(f"\nDone. {total_rows:,} total rows exported to: {os.path.abspath(OUT_DIR)}")

if __name__ == "__main__":
    export_all()
