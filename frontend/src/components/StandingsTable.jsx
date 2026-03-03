import React from "react";

export default function StandingsTable({ data, type }) {
  if (!data || !data.length) return <p className="text-gray-400">No standings data.</p>;

  // Get latest round per entity
  const latestRound = Math.max(...data.map((d) => d.round));
  const latest = data
    .filter((d) => d.round === latestRound)
    .sort((a, b) => a.position - b.position);

  const isDriver = type === "driver";

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm text-left border-collapse">
        <thead>
          <tr className="border-b border-f1gray text-gray-400 text-xs uppercase">
            <th className="py-2 pr-4">Pos</th>
            <th className="py-2 pr-4">{isDriver ? "Driver" : "Constructor"}</th>
            {isDriver && <th className="py-2 pr-4">Team</th>}
            <th className="py-2 pr-4 text-right">Points</th>
            <th className="py-2 text-right">Wins</th>
          </tr>
        </thead>
        <tbody>
          {latest.map((row, i) => (
            <tr
              key={i}
              className="border-b border-[#2a2a3a] hover:bg-[#1f1f2e] transition-colors"
            >
              <td className="py-2 pr-4 font-bold text-gray-300">{row.position}</td>
              <td className="py-2 pr-4 font-semibold">
                {isDriver ? (
                  <span>
                    <span className="text-gray-400 font-mono mr-2">{row.driver_code}</span>
                    {row.driver_name}
                  </span>
                ) : (
                  row.team_name || row.team_id
                )}
              </td>
              {isDriver && (
                <td className="py-2 pr-4 text-gray-400 text-xs">{row.team_id}</td>
              )}
              <td className="py-2 pr-4 text-right font-bold text-yellow-400">{row.points}</td>
              <td className="py-2 text-right text-gray-300">{row.wins}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
