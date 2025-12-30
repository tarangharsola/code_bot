import React from "react";

export default function Footer() {
  return (
    <footer className="container" style={{ padding: "2rem 0", textAlign: "center", fontSize: "0.95rem", color: "var(--text-muted)" }}>
      <span>&copy; {new Date().getFullYear()} Professional Website. All rights reserved.</span>
    </footer>
  );
}
