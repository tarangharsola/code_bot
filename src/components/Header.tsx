import React from "react";

export default function Header() {
  return (
    <header className="container" style={{ paddingTop: "1.5rem", paddingBottom: "1.5rem" }}>
      <nav style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <span style={{ fontWeight: 700, fontSize: "1.25rem" }}>Professional Website</span>
        <div>
          <a href="#about" style={{ marginRight: "1.5rem" }}>About</a>
          <a href="#contact">Contact</a>
        </div>
      </nav>
    </header>
  );
}
