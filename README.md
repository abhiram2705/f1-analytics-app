# F1 Analytics App

Full-stack Formula 1 race analytics:
- **Backend**: Python + FastAPI + FastF1 + SQL Server
- **Frontend**: React + Vite + Recharts + Tailwind CSS
- **BI**: Power BI Desktop connected directly to SQL Server

## Quick Start

### 1. Prerequisites
- [SQL Server Express](https://www.microsoft.com/en-us/sql-server/sql-server-downloads) (free)
- Python 3.11+
- Node.js 18+
- [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

### 2. Create the database
In SQL Server Management Studio or sqlcmd:
```sql
CREATE DATABASE f1_analytics;
```

### 3. Backend setup
```bash
cd backend
pip install -r requirements.txt
copy .env.example .env
# Edit .env — set DATABASE_URL to your SQL Server instance
uvicorn app.main:app --reload
```
The API auto-creates all tables on first startup.

API docs: http://localhost:8000/docs

### 4. Frontend setup
```bash
cd frontend
npm install
npm run dev
```
Open: http://localhost:5173

### 5. Import your first race
On the Dashboard page, enter a Season (e.g. 2024) and Round (e.g. 1), then click **Import Race**.
FastF1 downloads the official timing data (~1-2 min per race, cached after first download).

### 6. Power BI
Run `powerbi/views.sql` against your SQL Server, then follow `powerbi/README.md`.

---

## Features
| Feature | Where |
|---------|-------|
| Fastest lap per driver + sector times | Race Analysis → Fastest Laps |
| Tyre degradation curves by compound | Race Analysis → Tyre Degradation |
| Pit stop Gantt + stint strategy | Race Analysis → Pit Stop Strategy |
| Race pace rolling average | Race Analysis → Race Pace |
| Full race classification | Race Analysis → Results |
| Driver + constructor standings | Standings page |
| Power BI dashboard | `powerbi/` folder |

## Data Source
[FastF1](https://docs.fastf1.dev/) — Python library for official F1 timing data.
Supports all races from 2018 onwards.

