import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import { DashboardPage } from "./pages/DashboardPage";
import { LeadDetailPage } from "./pages/LeadDetailPage";

export default function App() {
  return (
    <BrowserRouter>
      <div className="container">
        <nav>
          <Link to="/">Dashboard</Link>
        </nav>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/leads/:id" element={<LeadDetailPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
