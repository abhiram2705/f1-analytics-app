import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getSeasons, getRaces, ingestRace } from "../api/f1api";

export default function Dashboard() {
  const [seasons, setSeasons] = useState([]);
  const [selectedSeason, setSelectedSeason] = useState(2024);
  const [races, setRaces] = useState([]);
  const [ingestSeason, setIngestSeason] = useState(2024);
  const [ingestRound, setIngestRound] = useState(1);
  const [ingestStatus, setIngestStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    getSeasons().then(setSeasons).catch(console.error);
  }, []);

  useEffect(() => {
    getRaces(selectedSeason).then(setRaces).catch(console.error);
  }, [selectedSeason]);

  const handleIngest = async () => {
    setLoading(true);
    setIngestStatus("Downloading session data from FastF1… (may take a minute)");
    try {
      const res = await ingestRace(ingestSeason, ingestRound);
      setIngestStatus(`✓ ${res.message} — ${res.laps_inserted} laps, ${res.stints_inserted} stints, ${res.pit_stops_inserted} pit stops`);
      // Refresh races
      getRaces(selectedSeason).then(setRaces);
    } catch (e) {
      setIngestStatus(`✗ Error: ${e.response?.data?.detail || e.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-1">Dashboard</h1>
      <p className="text-gray-400 mb-6">F1 Race Analytics</p>

      {/* Ingest panel */}
      <div className="bg-[#1f1f2e] rounded-lg p-5 mb-8 border border-f1gray">
        <h2 className="text-lg font-semibold mb-3 text-f1red">Import Race Data</h2>
        <div className="flex flex-wrap gap-3 items-end">
          <div>
            <label className="block text-xs text-gray-400 mb-1">Season</label>
            <input
              type="number"
              className="bg-f1gray text-white px-3 py-2 rounded border border-gray-600 w-24 focus:outline-none"
              value={ingestSeason}
              onChange={(e) => setIngestSeason(Number(e.target.value))}
              min={2018}
              max={2025}
            />
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Round</label>
            <input
              type="number"
              className="bg-f1gray text-white px-3 py-2 rounded border border-gray-600 w-20 focus:outline-none"
              value={ingestRound}
              onChange={(e) => setIngestRound(Number(e.target.value))}
              min={1}
              max={24}
            />
          </div>
          <button
            className="bg-f1red hover:bg-red-700 text-white px-5 py-2 rounded font-semibold disabled:opacity-50"
            onClick={handleIngest}
            disabled={loading}
          >
            {loading ? "Importing…" : "Import Race"}
          </button>
        </div>
        {ingestStatus && (
          <p className={`mt-3 text-sm ${ingestStatus.startsWith("✓") ? "text-green-400" : "text-yellow-400"}`}>
            {ingestStatus}
          </p>
        )}
        <p className="text-xs text-gray-500 mt-2">
          Data is fetched via FastF1 and cached locally. First import may take ~1–2 min.
        </p>
      </div>

      {/* Race grid */}
      <div className="flex items-center gap-4 mb-4">
        <h2 className="text-lg font-semibold">Races</h2>
        <select
          className="bg-f1gray text-white px-3 py-1.5 rounded border border-gray-600 text-sm focus:outline-none"
          value={selectedSeason}
          onChange={(e) => setSelectedSeason(Number(e.target.value))}
        >
          {seasons.map((s) => <option key={s.year} value={s.year}>{s.year}</option>)}
        </select>
      </div>

      {races.length === 0 ? (
        <p className="text-gray-500">No races imported yet. Use the importer above to get started.</p>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
          {races.map((r) => (
            <button
              key={r.race_id}
              onClick={() => navigate(`/race/${r.race_id}`)}
              className="bg-[#1f1f2e] hover:bg-f1gray border border-f1gray rounded-lg p-4 text-left transition-colors"
            >
              <p className="text-xs text-f1red font-bold">Rd {r.round}</p>
              <p className="font-semibold text-sm mt-1 leading-tight">{r.name}</p>
              {r.circuit && (
                <p className="text-xs text-gray-400 mt-1">{r.circuit.country}</p>
              )}
              {r.date && (
                <p className="text-xs text-gray-500 mt-1">{r.date}</p>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
