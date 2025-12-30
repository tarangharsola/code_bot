import React from "react";
import { createRoot } from "react-dom/client";
import App from "./components/App";
import "./styles/base.css";
import "./styles/theme.css";

const root = createRoot(document.getElementById("root")!);
root.render(<App />);
