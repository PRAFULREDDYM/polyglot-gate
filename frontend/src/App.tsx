import { Navigate, Route, Routes } from "react-router-dom";

import { NavBar } from "./components/NavBar";
import { EvaluationResults } from "./pages/EvaluationResults";
import { ModerationFlags } from "./pages/ModerationFlags";
import { SubmitPrompt } from "./pages/SubmitPrompt";
import { TriageDashboard } from "./pages/TriageDashboard";

export default function App() {
  return (
    <>
      <NavBar />
      <main>
        <Routes>
          <Route path="/" element={<Navigate to="/submit" replace />} />
          <Route path="/submit" element={<SubmitPrompt />} />
          <Route path="/results" element={<EvaluationResults />} />
          <Route path="/moderation" element={<ModerationFlags />} />
          <Route path="/triage" element={<TriageDashboard />} />
        </Routes>
      </main>
    </>
  );
}
