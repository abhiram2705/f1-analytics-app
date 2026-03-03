import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getSeasons, getRaces } from "../api/f1api";

export default function RaceSelector({ onSelect }) {
  const [seasons, setSeasons] = useState([]);
  const [selectedSeason, setSelectedSeason] = useState(2024);
  const [races, setRaces] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    getSeasons().then(setSeasons).catch(console.error);
  }, []);

  useEffect(() => {
    getRaces(selectedSeason).then(setRaces).catch(console.error);
  }, [selectedSeason]);

  return (
    <div className="flex flex-wrap gap-4 items-end mb-6">
      <div>
        <label className="block text-xs text-gray-400 mb-1">Season</label>
        <select
          className="bg-f1gray text-white px-3 py-2 rounded border border-gray-600 focus:outline-none"
          value={selectedSeason}
          onChange={(e) => setSelectedSeason(Number(e.target.value))}
        >
          {seasons.map((s) => (
            <option key={s.year} value={s.year}>{s.year}</option>
          ))}
        </select>
      </div>
      <div>
        <label className="block text-xs text-gray-400 mb-1">Race</label>
        <select
          className="bg-f1gray text-white px-3 py-2 rounded border border-gray-600 focus:outline-none min-w-[220px]"
          onChange={(e) => {
            const id = e.target.value;
            if (id) {
              navigate(`/race/${id}`);
              onSelect && onSelect(id);
            }
          }}
          defaultValue=""
        >
          <option value="" disabled>Select a race…</option>
          {races.map((r) => (
            <option key={r.race_id} value={r.race_id}>
              Rd {r.round} — {r.name}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
