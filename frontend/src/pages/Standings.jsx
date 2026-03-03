import React, { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from "recharts";
import { getDriverStandings, getConstructorStandings } from "../api/f1api";
import StandingsTable from "../components/StandingsTable";

const PALETTE = [
  "#e10600", "#00d2be", "#ff8700", "#0090ff", "#ffffff",
  "#960000", "#006f62", "#2b4562", "#ff87bc", "#b6babd",
  "#52e252", "#9b0000", "#3671c6", "#43b02a",
];

export default function Standings() {
  const [season, setSeason] = useState(2024);
  const [tab, setTab] = useState("drivers");
  const [driverData, setDriverData] = useState([]);
  const [constructorData, setConstructorData] = useState([]);

  useEffect(() => {
    getDriverStandings(season).then(setDriverData).catch(console.error);
    getConstructorStandings(season).then(setConstructorData).catch(console.error);
  }, [season]);

  const isDriver = tab === "drivers";
  const data = isDriver ? driverData : constructorData;
  const entityKey = isDriver ? "driver_code" : "team_id";
  const entities = [...new Set(data.map((d) => d[entityKey]))];

  // Pivot for chart
  const byRound = {};
  for (const row of data) {
    if (!byRound[row.round]) byRound[row.round] = { round: row.round };
    byRound[row.round][row[entityKey]] = row.points;
  }
  const chartData = Object.values(byRound).sort((a, b) => a.round - b.round);

  return (
    <div>
      <div className="flex items-center gap-4 mb-6">
        <h1 className="text-3xl font-bold">Standings</h1>
        <input
          type="number"
          className="bg-f1gray text-white px-3 py-1.5 rounded border border-gray-600 w-24 focus:outline-none"
          value={season}
          onChange={(e) => setSeason(Number(e.target.value))}
          min={2018}
          max={2025}
        />
      </div>

      {/* Toggle */}
      <div className="flex gap-1 mb-6 border-b border-f1gray">
        {["drivers", "constructors"].map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors capitalize ${
              tab === t ? "border-f1red text-white" : "border-transparent text-gray-400 hover:text-white"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Table */}
        <div className="bg-[#1f1f2e] rounded-lg p-5 border border-f1gray">
          <h2 className="text-lg font-semibold mb-4">Current Standings</h2>
          <StandingsTable data={data} type={tab === "drivers" ? "driver" : "constructor"} />
        </div>

        {/* Points progression chart */}
        <div className="bg-[#1f1f2e] rounded-lg p-5 border border-f1gray">
          <h2 className="text-lg font-semibold mb-4">Points Progression</h2>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={360}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#38383f" />
                <XAxis dataKey="round" stroke="#aaa" label={{ value: "Round", position: "insideBottom", offset: -5, fill: "#aaa", fontSize: 11 }} />
                <YAxis stroke="#aaa" />
                <Tooltip contentStyle={{ background: "#1f1f2e", border: "1px solid #38383f" }} />
                <Legend />
                {entities.map((e, i) => (
                  <Line
                    key={e}
                    type="monotone"
                    dataKey={e}
                    stroke={PALETTE[i % PALETTE.length]}
                    dot={false}
                    strokeWidth={2}
                    connectNulls
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-400">No data. Import races first.</p>
          )}
        </div>
      </div>
    </div>
  );
}
