# Power BI Integration Guide

## Prerequisites
- Power BI Desktop (free) — download from microsoft.com/en-us/power-bi/desktop
- SQL Server (or SQL Server Express) with the `f1_analytics` database populated
- ODBC Driver 17 for SQL Server (usually pre-installed on Windows)

---

## Step 1 — Create the SQL Views

Open **SQL Server Management Studio (SSMS)** or the Query Editor in Azure Data Studio,
connect to your instance, and run:

```
powerbi/views.sql
```

This creates 8 pre-joined views that Power BI can query directly:
| View | Contents |
|------|----------|
| `vw_fastest_laps` | Best lap per driver per race |
| `vw_tyre_degradation` | All clean laps with compound + tyre age |
| `vw_pit_strategy` | Pit stop events |
| `vw_stints` | Stint windows per driver |
| `vw_race_results` | Final race classification |
| `vw_driver_standings` | Points per driver per round |
| `vw_constructor_standings` | Points per team per round |
| `vw_all_laps` | Every lap (use with slicers) |

---

## Step 2 — Connect Power BI to SQL Server

1. Open **Power BI Desktop**
2. Click **Home → Get Data → SQL Server**
3. Enter your server name:
   - SQL Server Express: `localhost\SQLEXPRESS`
   - Full SQL Server: `localhost`
4. Database: `f1_analytics`
5. Data Connectivity mode: **Import** (for best performance) or **DirectQuery** (for live data)
6. Click **OK** and authenticate (Windows Authentication works out of the box)
7. In the Navigator, expand the **Views** folder and select the ones you need
8. Click **Load** or **Transform Data**

---

## Step 3 — Suggested Report Pages

### Page 1: Season Overview
- **Slicer**: season (from `vw_driver_standings`)
- **Line Chart**: points by round, legend = driver_code (from `vw_driver_standings`)
- **Table**: Current standings (filter to max round)

### Page 2: Fastest Laps
- **Slicer**: race_name (from `vw_fastest_laps`)
- **Bar Chart**: driver_code on axis, lap_time_sec on value, colored by team_name
- **Table**: full fastest lap table with s1/s2/s3 sectors

### Page 3: Tyre Strategy
- **Slicer**: race_name, compound
- **Line Chart**: lap_time_sec by tyre_life, each line = compound (from `vw_tyre_degradation`)
- **Stacked Bar**: stint_length by driver, segment = compound (from `vw_stints`)

### Page 4: Pit Stop Analysis
- **Slicer**: race_name
- **Scatter Plot**: duration_sec by lap, color = team_name
- **Bar Chart**: avg pit duration by team_name

### Page 5: Driver Head-to-Head
- Use **Parameters** (What-If) to pick Driver 1 and Driver 2
- Line chart of lap_time_sec per lap for each driver side by side

---

## Useful DAX Measures

Paste these in **Modeling → New Measure**:

```dax
-- Average pit stop duration in seconds
Avg Pit Duration (s) =
    AVERAGE(vw_pit_strategy[duration_sec])

-- Median lap time
Median Lap Time (s) =
    MEDIAN(vw_tyre_degradation[lap_time_sec])

-- Points leader
Points Leader =
    MAXX(
        TOPN(1, vw_driver_standings, vw_driver_standings[points], DESC),
        vw_driver_standings[driver_name]
    )

-- Delta from fastest lap
Delta From Fastest (ms) =
    [Lap Time (ms)] - MINX(
        FILTER(vw_fastest_laps, vw_fastest_laps[race_id] = SELECTEDVALUE(vw_fastest_laps[race_id])),
        vw_fastest_laps[lap_time_ms]
    )

-- Tyre degradation rate (slope: ms per lap on tyre)
Deg Rate =
    DIVIDE(
        MAXX(vw_tyre_degradation, vw_tyre_degradation[lap_time_sec]) -
        MINX(vw_tyre_degradation, vw_tyre_degradation[lap_time_sec]),
        MAXX(vw_tyre_degradation, vw_tyre_degradation[tyre_life]) - 1
    )
```

---

## Data Model Relationships (set these in Model view)

| From | To | Cardinality |
|------|----|-------------|
| `vw_all_laps[race_id]` | `vw_race_results[race_id]` | Many-to-many (via race) |
| `vw_driver_standings[driver_id]` | `vw_fastest_laps[driver_id]` | Many-to-many |

Power BI will auto-detect most relationships if you load from the same SQL Server source.
Use the **Manage Relationships** dialog to verify or add cross-view filters.

---

## Refreshing Data

1. Import new race data via the web app (Dashboard → Import Race)
2. In Power BI: **Home → Refresh** to pull latest data from SQL Server
3. For scheduled refresh, publish to **Power BI Service** and configure a gateway
