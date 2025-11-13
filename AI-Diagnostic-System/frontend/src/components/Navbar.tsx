import React from "react";
import { Link, useLocation } from "react-router-dom";

const Navbar: React.FC = () => {
  const location = useLocation();

  const isActive = (path: string) =>
    location.pathname === path
      ? "text-primary font-semibold border-b-2 border-primary"
      : "text-gray-700 hover:text-primary transition";

  return (
    <nav className="w-full bg-surface shadow-soft px-6 py-3 flex justify-between items-center sticky top-0 z-50">
      <h1 className="text-xl font-bold text-primary tracking-wide">
        IrisAI Diagnósticos
      </h1>

      <div className="flex gap-6">
        <Link to="/" className={isActive("/")}>
          Início
        </Link>
        <Link to="/history" className={isActive("/history")}>
          Histórico
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;
