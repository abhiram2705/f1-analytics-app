import React from "react";
import { Outlet, NavLink } from "react-router-dom";

export default function Layout() {
  const linkClass = ({ isActive }) =>
    `px-4 py-2 rounded text-sm font-semibold transition-colors ${
      isActive ? "bg-f1red text-white" : "text-gray-300 hover:text-white"
    }`;

  return (
    <div className="min-h-screen bg-f1dark text-white">
      {/* Top nav */}
      <nav className="border-b border-f1gray bg-[#1f1f2e] px-6 py-3 flex items-center gap-6">
        <span className="text-f1red font-bold text-xl tracking-widest mr-4">F1 ANALYTICS</span>
        <NavLink to="/" end className={linkClass}>Dashboard</NavLink>
        <NavLink to="/standings" className={linkClass}>Standings</NavLink>
      </nav>

      <main className="px-6 py-6 max-w-screen-2xl mx-auto">
        <Outlet />
      </main>
    </div>
  );
}
