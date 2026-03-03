import React, { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import { getFastestLaps } from "../api/f1api";

const TEAM_COLORS = {
  red_bull: "#3671C6",
  ferrari: "#E8002D",
  mercedes: "#27F4D2",
  mclaren: "#FF8000",
  aston_martin: "#229971",
  alpine: "#FF87BC",
  williams: "#64C4FF",
  rb: "#6692FF",
  haas: "#B6BABD",
  kick_sauber: "#52E252",
};

const msToTime = (ms) => {
  if (!ms) return "N/A";
  const totalSec = ms / 1000;
  const mins = Math.floor(totalSec / 60);
  const secs = (totalSec % 60).toFixed(3);
  return `${mins}:${secs.padStart(6, "0")}`;
};

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-[#1f1f2e] border border-f1gray p-3 rounded text-xs">
      <p className="font-bold">{d.driver_code} — {d.driver_name}</p>
      <p className="text-gray-300">{d.team_name || d.team_id}</p>
      <p>Lap {d.lap_number}: <span className="text-yellow-400 font-mono">{msToTime(d.lap_time_ms)}</span></p>
      <p>Compound: <span style={{ color: compoundColor(d.compound) }}>{d.compound}</span></p>
    </div>
  );
};

const compoundColor = (c) => ({ SOFT: "#E8002D", MEDIUM: "#FFF200", HARD: "#FFFFFF", INTER: "#43B02A", WET: "#0067FF" }[c] || "#aaa");

export default function FastestLapChart({ raceId }) {
  const [data, setData] = useState([]);

  useEffect(() => {
    if (!raceId) return;
    getFastestLaps(raceId).then(setData).catch(console.error);
  }, [raceId]);

  if (!data.length) return <p className="text-gray-400">No data available.</p>;

  const leader = data[0]?.lap_time_ms || 1;

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">Fastest Lap per Driver</h3>
      <ResponsiveContainer width="100%" height={420}>
        <BarChart data={data} layout="vertical" margin={{ left: 20, right: 60 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#38383f" />
          <XAxis
            type="number"
            domain={[leader * 0.98, "auto"]}
            tickFormatter={(v) => msToTime(v)}
            stroke="#aaa"
            tick={{ fontSize: 11 }}
          />
          <YAxis
            type="category"
            dataKey="driver_code"
            stroke="#aaa"
            tick={{ fontSize: 12, fill: "#ddd" }}
            width={40}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="lap_time_ms" radius={[0, 4, 4, 0]}>
            {data.map((entry, i) => (
              <Cell
                key={i}
                fill={TEAM_COLORS[entry.team_id?.toLowerCase()] || "#888"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
