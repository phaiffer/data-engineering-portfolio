import { useEffect } from "react";
import { Dashboard } from "./features/Dashboard";

export default function App() {
  useEffect(() => {
    const isCaptureMode = new URLSearchParams(window.location.search).get("capture") === "1";
    document.documentElement.classList.toggle("capture-mode", isCaptureMode);

    return () => {
      document.documentElement.classList.remove("capture-mode");
    };
  }, []);

  return <Dashboard />;
}
