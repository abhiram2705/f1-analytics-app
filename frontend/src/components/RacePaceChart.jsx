import React, { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from "recharts";
import { getRacePace } from "../api/f1api";

const PALETTE = [
  "#e10600", "#00d2be", "#ff8700", "#0090ff", "#ffffff",
  "#960000", "#006f62", "#2b4562", "#ff87bc", "#b6babd",
  "#52e252", "#9b0000", "#3671c6", "#43b02a",
];

const msToSec = (ms) => ms ? +(ms / 1000).toFixed(3) : null;

export default function RacePaceChart({ raceId }) {
  const [rawData, setRawData] = useState([]);

  useEffect(() => {
    if (!raceId) return;
    getRacePace(raceId).then(setRawData).catch(console.error);
  }, [raceId]);

  if (!rawData.length) return <p className="text-gray-400">No data available.</p>;

  const drivers = [...new Set(rawData.map((d) => d.driver_code))];

  // Pivot by lap_number
  const byLap = {};
  for (const row of rawData) {
    if (!byLap[row.lap_number]) byLap[row.lap_number] = { lap: row.lap_number };
    byLap[row.lap_number][row.driver_code] = msToSec(row.rolling_avg_ms);
  }
  const chartData = Object.values(byLap).sort((a, b) => a.lap - b.lap);

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">Race Pace — 3-Lap Rolling Average</h3>
      <ResponsiveContainer width="100%" height={420}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#38383f" />
          <XAxis
            dataKey="lap"
            label={{ value: "Lap", position: "insideBottom", offset: -5, fill: "#aaa", fontSize: 12 }}
            stroke="#aaa"
          />
          <YAxis
            label={{ value: "Avg Lap Time (s)", angle: -90, position: "insideLeft", fill: "#aaa", fontSize: 12 }}
            stroke="#aaa"
            domain={["auto", "auto"]}
          />
          <Tooltip
            formatter={(v, name) => [`${v}s`, name]}
            contentStyle={{ background: "#1f1f2e", border: "1px solid #38383f" }}
          />
          <Legend />
          {drivers.map((drv, i) => (
            <Line
              key={drv}
              type="monotone"
              dataKey={drv}
              stroke={PALETTE[i % PALETTE.length]}
              dot={false}
              strokeWidth={1.5}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
