import React, { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from "recharts";
import { getTyreDegradation } from "../api/f1api";

const COMPOUND_COLORS = {
  SOFT: "#E8002D",
  MEDIUM: "#FFF200",
  HARD: "#FFFFFF",
  INTER: "#43B02A",
  WET: "#0067FF",
};

const msToSec = (ms) => ms ? (ms / 1000).toFixed(3) : null;

export default function TyreDegradationChart({ raceId }) {
  const [rawData, setRawData] = useState([]);

  useEffect(() => {
    if (!raceId) return;
    getTyreDegradation(raceId).then(setRawData).catch(console.error);
  }, [raceId]);

  if (!rawData.length) return <p className="text-gray-400">No data available.</p>;

  // Pivot: { tyre_life: number, SOFT: sec, MEDIUM: sec, ... }
  const compounds = [...new Set(rawData.map((d) => d.compound))];
  const byLife = {};
  for (const row of rawData) {
    if (!byLife[row.tyre_life]) byLife[row.tyre_life] = { tyre_life: row.tyre_life };
    byLife[row.tyre_life][row.compound] = parseFloat(msToSec(row.avg_lap_time_ms));
  }
  const chartData = Object.values(byLife).sort((a, b) => a.tyre_life - b.tyre_life);

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">Tyre Degradation — Avg Lap Time by Compound</h3>
      <ResponsiveContainer width="100%" height={380}>
        <LineChart data={chartData} margin={{ right: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#38383f" />
          <XAxis
            dataKey="tyre_life"
            label={{ value: "Tyre Age (laps)", position: "insideBottom", offset: -5, fill: "#aaa", fontSize: 12 }}
            stroke="#aaa"
          />
          <YAxis
            label={{ value: "Lap Time (s)", angle: -90, position: "insideLeft", fill: "#aaa", fontSize: 12 }}
            stroke="#aaa"
            domain={["auto", "auto"]}
          />
          <Tooltip
            formatter={(v, name) => [`${v}s`, name]}
            contentStyle={{ background: "#1f1f2e", border: "1px solid #38383f" }}
          />
          <Legend wrapperStyle={{ paddingTop: 16 }} />
          {compounds.map((c) => (
            <Line
              key={c}
              type="monotone"
              dataKey={c}
              stroke={COMPOUND_COLORS[c] || "#aaa"}
              dot={false}
              strokeWidth={2}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
