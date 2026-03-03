import React, { useEffect, useState } from "react";
import { getStints, getPitStops } from "../api/f1api";

const COMPOUND_COLORS = {
  SOFT: "#E8002D",
  MEDIUM: "#FFF200",
  HARD: "#FFFFFF",
  INTER: "#43B02A",
  WET: "#0067FF",
};

export default function PitStopTimeline({ raceId }) {
  const [stints, setStints] = useState([]);
  const [pitStops, setPitStops] = useState([]);

  useEffect(() => {
    if (!raceId) return;
    Promise.all([getStints(raceId), getPitStops(raceId)])
      .then(([s, p]) => { setStints(s); setPitStops(p); })
      .catch(console.error);
  }, [raceId]);

  if (!stints.length) return <p className="text-gray-400">No data available.</p>;

  // Group stints by driver
  const drivers = [...new Set(stints.map((s) => s.driver_id))];
  const maxLap = Math.max(...stints.map((s) => s.end_lap || 0), 70);

  const pitMap = {};
  for (const p of pitStops) {
    if (!pitMap[p.driver_id]) pitMap[p.driver_id] = [];
    pitMap[p.driver_id].push(p);
  }

  return (
    <div>
      <h3 className="text-lg font-semibold mb-2">Pit Stop Strategy</h3>
      <p className="text-xs text-gray-400 mb-4">Each bar = a stint. Color = compound. Markers = pit stops.</p>
      <div className="overflow-x-auto">
        <div className="min-w-[700px]">
          {/* Header */}
          <div className="flex items-center mb-1 text-xs text-gray-400">
            <div className="w-14 shrink-0">Driver</div>
            <div className="flex-1 relative h-4">
              {[0, 25, 50, 75, 100].map((p) => (
                <span
                  key={p}
                  className="absolute"
                  style={{ left: `${p}%`, transform: "translateX(-50%)" }}
                >
                  {Math.round((p / 100) * maxLap)}
                </span>
              ))}
            </div>
          </div>

          {drivers.map((driverId) => {
            const driverStints = stints.filter((s) => s.driver_id === driverId);
            const code = driverStints[0]?.driver_code || driverId.toUpperCase().slice(0, 3);
            const driverPits = pitMap[driverId] || [];

            return (
              <div key={driverId} className="flex items-center mb-2 h-7">
                <div className="w-14 shrink-0 text-xs font-mono text-gray-200">{code}</div>
                <div className="flex-1 relative h-5 bg-[#1f1f2e] rounded">
                  {driverStints.map((s, i) => {
                    const left = ((s.start_lap - 1) / maxLap) * 100;
                    const width = ((s.end_lap - s.start_lap + 1) / maxLap) * 100;
                    const color = COMPOUND_COLORS[s.compound] || "#555";
                    return (
                      <div
                        key={i}
                        title={`${s.compound} laps ${s.start_lap}–${s.end_lap}`}
                        className="absolute top-0.5 h-4 rounded opacity-90"
                        style={{ left: `${left}%`, width: `${width}%`, backgroundColor: color }}
                      />
                    );
                  })}
                  {driverPits.map((p, i) => {
                    const left = ((p.lap - 1) / maxLap) * 100;
                    return (
                      <div
                        key={i}
                        title={`Pit lap ${p.lap}${p.duration_ms ? ` (${(p.duration_ms / 1000).toFixed(1)}s)` : ""}`}
                        className="absolute top-0 h-5 w-0.5 bg-white opacity-70"
                        style={{ left: `${left}%` }}
                      />
                    );
                  })}
                </div>
              </div>
            );
          })}

          {/* Compound legend */}
          <div className="flex gap-4 mt-3 flex-wrap">
            {Object.entries(COMPOUND_COLORS).map(([c, col]) => (
              <span key={c} className="flex items-center gap-1 text-xs">
                <span className="inline-block w-3 h-3 rounded" style={{ backgroundColor: col }} />
                {c}
              </span>
            ))}
            <span className="flex items-center gap-1 text-xs">
              <span className="inline-block w-0.5 h-3 bg-white" />
              Pit stop
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
