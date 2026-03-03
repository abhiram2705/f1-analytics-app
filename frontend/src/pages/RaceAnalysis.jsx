import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getRace, getRaceResults } from "../api/f1api";
import FastestLapChart from "../components/FastestLapChart";
import TyreDegradationChart from "../components/TyreDegradationChart";
import PitStopTimeline from "../components/PitStopTimeline";
import RacePaceChart from "../components/RacePaceChart";

const TABS = ["Fastest Laps", "Tyre Degradation", "Pit Stop Strategy", "Race Pace", "Results"];

export default function RaceAnalysis() {
  const { raceId } = useParams();
  const navigate = useNavigate();
  const [race, setRace] = useState(null);
  const [results, setResults] = useState([]);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    if (!raceId) return;
    getRace(raceId).then(setRace).catch(console.error);
    getRaceResults(raceId).then(setResults).catch(console.error);
  }, [raceId]);

  return (
    <div>
      <button
        className="text-gray-400 hover:text-white text-sm mb-4 flex items-center gap-1"
        onClick={() => navigate("/")}
      >
        ← Back to Dashboard
      </button>

      {race ? (
        <div className="mb-6">
          <p className="text-f1red text-sm font-bold">Round {race.round} · {race.season}</p>
          <h1 className="text-3xl font-bold">{race.name}</h1>
          {race.circuit && (
            <p className="text-gray-400 text-sm mt-1">
              {race.circuit.name} · {race.circuit.city}, {race.circuit.country}
            </p>
          )}
          {race.date && <p className="text-gray-500 text-xs mt-0.5">{race.date}</p>}
        </div>
      ) : (
        <p className="text-gray-400 mb-6">Loading race info…</p>
      )}

      {/* Tab bar */}
      <div className="flex gap-1 mb-6 border-b border-f1gray">
        {TABS.map((tab, i) => (
          <button
            key={tab}
            onClick={() => setActiveTab(i)}
            className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 -mb-px ${
              activeTab === i
                ? "border-f1red text-white"
                : "border-transparent text-gray-400 hover:text-white"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="bg-[#1f1f2e] rounded-lg p-6 border border-f1gray">
        {activeTab === 0 && <FastestLapChart raceId={raceId} />}
        {activeTab === 1 && <TyreDegradationChart raceId={raceId} />}
        {activeTab === 2 && <PitStopTimeline raceId={raceId} />}
        {activeTab === 3 && <RacePaceChart raceId={raceId} />}
        {activeTab === 4 && <ResultsTab results={results} />}
      </div>
    </div>
  );
}

function ResultsTab({ results }) {
  if (!results.length) return <p className="text-gray-400">No results data.</p>;
  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">Race Results</h3>
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="text-xs uppercase text-gray-400 border-b border-f1gray">
            <th className="py-2 pr-3 text-left">Pos</th>
            <th className="py-2 pr-3 text-left">Driver</th>
            <th className="py-2 pr-3 text-left">Team</th>
            <th className="py-2 pr-3 text-right">Grid</th>
            <th className="py-2 pr-3 text-right">Points</th>
            <th className="py-2 text-left">Status</th>
          </tr>
        </thead>
        <tbody>
          {results.map((r, i) => (
            <tr key={i} className="border-b border-[#2a2a3a] hover:bg-[#282838]">
              <td className="py-2 pr-3 font-bold">{r.position ?? "–"}</td>
              <td className="py-2 pr-3">
                <span className="text-gray-400 font-mono mr-2 text-xs">{r.driver_code}</span>
                {r.driver_name}
              </td>
              <td className="py-2 pr-3 text-gray-400 text-xs">{r.team_name || r.team_id}</td>
              <td className="py-2 pr-3 text-right text-gray-400">{r.grid ?? "–"}</td>
              <td className="py-2 pr-3 text-right font-bold text-yellow-400">{r.points}</td>
              <td className="py-2 text-xs text-gray-400">{r.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
