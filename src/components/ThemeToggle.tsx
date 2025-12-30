import React, { useEffect, useState } from "react";

function getSystemTheme() {
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export default function ThemeToggle() {
  const [theme, setTheme] = useState(() => localStorage.getItem("theme") || getSystemTheme());

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  useEffect(() => {
    const listener = (e: MediaQueryListEvent) => {
      if (!localStorage.getItem("theme")) setTheme(e.matches ? "dark" : "light");
    };
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", listener);
    return () => window.matchMedia("(prefers-color-scheme: dark)").removeEventListener("change", listener);
  }, []);

  return (
    <button
      aria-label="Toggle theme"
      style={{
        position: "fixed",
        right: "1.5rem",
        bottom: "1.5rem",
        background: "var(--bg-elevated)",
        color: "var(--text)",
        border: "none",
        borderRadius: "50%",
        width: "44px",
        height: "44px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
        cursor: "pointer",
        fontSize: "1.25rem",
        zIndex: 1000,
        transition: "background 0.2s"
      }}
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
    >
      {theme === "dark" ? "🌞" : "🌙"}
    </button>
  );
}
