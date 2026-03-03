-- ============================================================
-- F1 Analytics — SQL Server Views for Power BI
-- Run this script once against your f1_analytics database.
-- ============================================================

USE f1_analytics;
GO

-- ---- 1. Fastest Laps View ----
CREATE OR ALTER VIEW vw_fastest_laps AS
SELECT
    r.race_id,
    r.season,
    r.round,
    r.name         AS race_name,
    r.date         AS race_date,
    ci.name        AS circuit_name,
    ci.country,
    d.driver_id,
    d.code         AS driver_code,
    d.full_name    AS driver_name,
    d.team_id,
    co.name        AS team_name,
    l.lap_number,
    l.lap_time_ms,
    l.lap_time_ms / 1000.0  AS lap_time_sec,
    l.s1_ms / 1000.0        AS s1_sec,
    l.s2_ms / 1000.0        AS s2_sec,
    l.s3_ms / 1000.0        AS s3_sec,
    l.compound
FROM laps l
JOIN races r    ON r.race_id  = l.race_id
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
  );
GO

-- ---- 2. Tyre Degradation View ----
CREATE OR ALTER VIEW vw_tyre_degradation AS
SELECT
    r.race_id,
    r.season,
    r.round,
    r.name         AS race_name,
    r.date         AS race_date,
    d.driver_id,
    d.code         AS driver_code,
    d.team_id,
    co.name        AS team_name,
    l.compound,
    l.tyre_life,
    l.lap_time_ms / 1000.0  AS lap_time_sec,
    l.lap_number
FROM laps l
JOIN races r    ON r.race_id   = l.race_id
JOIN drivers d  ON d.driver_id = l.driver_id
LEFT JOIN constructors co ON co.team_id = d.team_id
WHERE l.lap_time_ms IS NOT NULL
  AND l.compound    IS NOT NULL
  AND l.tyre_life   IS NOT NULL
  AND l.track_status IN ('1', NULL);
GO

-- ---- 3. Pit Stop Strategy View ----
CREATE OR ALTER VIEW vw_pit_strategy AS
SELECT
    p.pit_id,
    r.race_id,
    r.season,
    r.round,
    r.name          AS race_name,
    r.date          AS race_date,
    d.driver_id,
    d.code          AS driver_code,
    d.full_name     AS driver_name,
    d.team_id,
    co.name         AS team_name,
    p.stop_number,
    p.lap,
    p.duration_ms,
    p.duration_ms / 1000.0 AS duration_sec
FROM pit_stops p
JOIN races r    ON r.race_id   = p.race_id
JOIN drivers d  ON d.driver_id = p.driver_id
LEFT JOIN constructors co ON co.team_id = d.team_id;
GO

-- ---- 4. Stints View ----
CREATE OR ALTER VIEW vw_stints AS
SELECT
    s.stint_id,
    r.race_id,
    r.season,
    r.round,
    r.name          AS race_name,
    r.date          AS race_date,
    d.driver_id,
    d.code          AS driver_code,
    d.full_name     AS driver_name,
    d.team_id,
    co.name         AS team_name,
    s.stint_number,
    s.compound,
    s.start_lap,
    s.end_lap,
    (s.end_lap - s.start_lap + 1) AS stint_length
FROM stints s
JOIN races r    ON r.race_id   = s.race_id
JOIN drivers d  ON d.driver_id = s.driver_id
LEFT JOIN constructors co ON co.team_id = d.team_id;
GO

-- ---- 5. Race Results View ----
CREATE OR ALTER VIEW vw_race_results AS
SELECT
    rr.result_id,
    r.race_id,
    r.season,
    r.round,
    r.name          AS race_name,
    r.date          AS race_date,
    ci.name         AS circuit_name,
    ci.country,
    d.driver_id,
    d.code          AS driver_code,
    d.full_name     AS driver_name,
    d.team_id,
    co.name         AS team_name,
    rr.position,
    rr.grid,
    rr.points,
    rr.status,
    rr.fastest_lap_rank,
    rr.fastest_lap_time_ms / 1000.0 AS fastest_lap_time_sec
FROM race_results rr
JOIN races r    ON r.race_id   = rr.race_id
JOIN drivers d  ON d.driver_id = rr.driver_id
LEFT JOIN circuits ci     ON ci.circuit_id = r.circuit_id
LEFT JOIN constructors co ON co.team_id    = d.team_id;
GO

-- ---- 6. Driver Standings View ----
CREATE OR ALTER VIEW vw_driver_standings AS
SELECT
    ds.id,
    ds.season,
    ds.round,
    r.name          AS race_name,
    d.driver_id,
    d.code          AS driver_code,
    d.full_name     AS driver_name,
    d.team_id,
    co.name         AS team_name,
    ds.position,
    ds.points,
    ds.wins
FROM driver_standings ds
JOIN drivers d  ON d.driver_id = ds.driver_id
LEFT JOIN constructors co ON co.team_id = d.team_id
LEFT JOIN races r ON r.season = ds.season AND r.round = ds.round;
GO

-- ---- 7. Constructor Standings View ----
CREATE OR ALTER VIEW vw_constructor_standings AS
SELECT
    cs.id,
    cs.season,
    cs.round,
    r.name          AS race_name,
    cs.team_id,
    co.name         AS team_name,
    cs.position,
    cs.points,
    cs.wins
FROM constructor_standings cs
LEFT JOIN constructors co ON co.team_id = cs.team_id
LEFT JOIN races r ON r.season = cs.season AND r.round = cs.round;
GO

-- ---- 8. All Laps (full detail) ----
CREATE OR ALTER VIEW vw_all_laps AS
SELECT
    l.lap_id,
    r.race_id,
    r.season,
    r.round,
    r.name          AS race_name,
    r.date          AS race_date,
    d.driver_id,
    d.code          AS driver_code,
    d.full_name     AS driver_name,
    d.team_id,
    co.name         AS team_name,
    l.lap_number,
    l.lap_time_ms / 1000.0  AS lap_time_sec,
    l.s1_ms  / 1000.0       AS s1_sec,
    l.s2_ms  / 1000.0       AS s2_sec,
    l.s3_ms  / 1000.0       AS s3_sec,
    l.compound,
    l.tyre_life,
    l.is_personal_best,
    l.track_status
FROM laps l
JOIN races r    ON r.race_id   = l.race_id
JOIN drivers d  ON d.driver_id = l.driver_id
LEFT JOIN constructors co ON co.team_id = d.team_id;
GO
