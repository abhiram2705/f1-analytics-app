# Power BI Dashboard Setup — F1 Analytics

## Step 1 — Install Power BI Desktop (Free)

1. Go to: https://powerbi.microsoft.com/desktop
2. Click **Download free** → download the installer
3. Run the installer (no account needed for Desktop mode)

---

## Step 2 — Load the CSV Data Files

All CSV files are in:
```
C:\Users\abhir\Documents\f1-analytics\powerbi\data\
```

| File | Rows | Contents |
|------|------|----------|
| `fastest_laps.csv` | 59 | Best lap per driver per race |
| `tyre_degradation.csv` | 2,955 | Every clean lap with compound + tyre age |
| `pit_stops.csv` | 104 | Pit stop events |
| `stints.csv` | 164 | Stint windows per driver |
| `race_results.csv` | 60 | Final race classification |
| `all_laps.csv` | 3,043 | All valid lap times |

### Load steps:
1. Open Power BI Desktop
2. Click **Home → Get Data → Text/CSV**
3. Navigate to the `data\` folder and select **all 6 CSV files** one by one
   (repeat Get Data for each file)
4. For each file Power BI will preview it — click **Load**
5. After loading all 6, go to **Model view** (left sidebar, middle icon)

---

## Step 3 — Set Up Relationships (Model View)

In the **Model view**, drag and drop to create these relationships:

| From table → column | To table → column | Cardinality |
|---------------------|-------------------|-------------|
| `all_laps` → race_name | `fastest_laps` → race_name | Many to Many |
| `all_laps` → driver_code | `fastest_laps` → driver_code | Many to Many |
| `tyre_degradation` → race_name | `stints` → race_name | Many to Many |
| `pit_stops` → race_name | `stints` → race_name | Many to Many |

> Tip: For a simpler model, use **race_name + driver_code** as the join keys
> across all tables since they appear in every file.

---

## Step 4 — Build the Report Pages

### Page 1: Fastest Laps

1. Add a **Slicer** visual → drag `fastest_laps[race_name]` into it
2. Add a **Bar Chart**:
   - Y-axis: `driver_code`
   - X-axis: `lap_time_sec`
   - Legend: `team_name`
3. Add a **Table** visual with columns:
   - `driver_code`, `driver_name`, `team_name`, `lap_time_sec`, `s1_sec`, `s2_sec`, `s3_sec`, `compound`
4. Sort the bar chart by `lap_time_sec` ascending
5. Format bar colors by team:
   - Click bar chart → Format → Data colors → set manually:
     - Red Bull Racing: `#3671C6`
     - Ferrari: `#E8002D`
     - Mercedes: `#27F4D2`
     - McLaren: `#FF8000`
     - Aston Martin: `#229971`

---

### Page 2: Tyre Degradation

1. Add a **Slicer** → `tyre_degradation[race_name]`
2. Add a **Slicer** → `tyre_degradation[compound]`
3. Add a **Line Chart**:
   - X-axis: `tyre_life`
   - Y-axis: Average of `lap_time_sec`
   - Legend: `compound`
4. Format line colors:
   - SOFT: `#E8002D`
   - MEDIUM: `#FFF200`
   - HARD: `#C0C0C0`
5. Add a **Card** visual → Min of `lap_time_sec` (fastest clean lap)
6. Add a **Card** visual → Max of `tyre_life` (longest stint)

**New Measure for degradation rate:**
- Go to **Home → New Measure**
```
Deg Rate (s/lap) =
DIVIDE(
    MAXX(tyre_degradation, tyre_degradation[lap_time_sec]) -
    MINX(tyre_degradation, tyre_degradation[lap_time_sec]),
    MAXX(tyre_degradation, tyre_degradation[tyre_life]) - 1
)
```

---

### Page 3: Pit Stop Strategy (Gantt)

1. Add a **Slicer** → `stints[race_name]`
2. Install the **Gantt Chart** visual (free):
   - Click **...** in the Visualizations pane → Get more visuals
   - Search "Gantt" → add **Gantt Chart by MAQ Software**
3. Configure Gantt:
   - Task: `driver_code`
   - Start Date: `start_lap`
   - Duration: `stint_length`
   - Legend: `compound`
4. Add a **Table** for pit stops below:
   - Columns: `driver_code`, `team_name`, `stop_number`, `lap`, `duration_sec`
   - Sort by `lap` ascending
5. Add a **Bar Chart** for avg pit duration by team:
   - X-axis: `team_name`
   - Y-axis: Average of `duration_sec`

---

### Page 4: Race Pace

1. Add a **Slicer** → `all_laps[race_name]`
2. Add a **Multi-row card**:
   - Min `lap_time_sec` (fastest lap of race)
3. Add a **Line Chart** for pace per driver:
   - X-axis: `lap_number`
   - Y-axis: Average of `lap_time_sec`
   - Legend: `driver_code`

**Rolling 3-lap average measure:**
```
Rolling Avg Pace =
AVERAGEX(
    FILTER(
        all_laps,
        all_laps[driver_code] = SELECTEDVALUE(all_laps[driver_code]) &&
        all_laps[lap_number] >= MAX(all_laps[lap_number]) - 2 &&
        all_laps[lap_number] <= MAX(all_laps[lap_number])
    ),
    all_laps[lap_time_sec]
)
```

4. Add a **Scatter Chart** — lap_time_sec vs tyre_life, colored by compound

---

### Page 5: Race Results

1. Add a **Slicer** → `race_results[race_name]`
2. Add a **Table**:
   - `position`, `driver_code`, `driver_name`, `team_name`, `grid`, `points`, `status`
   - Conditional formatting on `position` (green = P1, red = DNF)
3. Add a **Clustered Bar Chart**:
   - X-axis: `points`
   - Y-axis: `driver_code`
   - Sorted descending by points

---

## Step 5 — Apply F1 Dark Theme

1. Click **View → Themes → Customize current theme**
2. Set:
   - Background: `#15151E`
   - Text: `#FFFFFF`
   - Accent 1: `#E10600` (F1 red)
   - Data colors: add team colors array above

Or paste this JSON into **View → Themes → Browse for themes**:

```json
{
  "name": "F1 Dark",
  "dataColors": ["#E8002D","#27F4D2","#FF8000","#3671C6","#229971","#FF87BC","#64C4FF","#6692FF","#B6BABD","#52E252"],
  "background": "#15151E",
  "foreground": "#FFFFFF",
  "tableAccent": "#E10600"
}
```
Save as `f1_theme.json` and import it.

---

## Step 6 — Refresh Data After Importing More Races

When you import more races via the web app:
1. Run the export script again from the backend folder:
   ```
   cd C:\Users\abhir\Documents\f1-analytics\backend
   venv\Scripts\python ..\powerbi\export_csv.py
   ```
2. In Power BI Desktop: **Home → Refresh**
3. All pages update automatically

---

## Quick Checklist

- [ ] Power BI Desktop installed
- [ ] All 6 CSVs loaded
- [ ] Relationships set (race_name, driver_code)
- [ ] Page 1: Fastest Laps bar chart
- [ ] Page 2: Tyre degradation lines by compound
- [ ] Page 3: Pit stop strategy Gantt
- [ ] Page 4: Race pace line chart
- [ ] Page 5: Results table
- [ ] F1 dark theme applied
