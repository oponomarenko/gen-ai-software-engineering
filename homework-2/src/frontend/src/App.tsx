import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { useState } from "react";
import { TicketList } from "./components/TicketList";
import { TicketDetail } from "./components/TicketDetail";
import { TicketForm } from "./components/TicketForm";
import { BulkImport } from "./components/BulkImport";
import { ToastContainer } from "./components/Toast";
import { useToast } from "./hooks/useToast";
import "./App.css";

function AppContent() {
  const { toasts, removeToast } = useToast();
  const [refreshList, setRefreshList] = useState(false);

  return (
    <>
      <header className="app-header">
        <nav className="navbar">
          <Link to="/" className="navbar-brand">
            Support Ticket System
          </Link>
          <div className="nav-links">
            <Link to="/" className="nav-link">
              Tickets
            </Link>
            <Link to="/import" className="nav-link">
              Import
            </Link>
          </div>
        </nav>
      </header>

      <main className="app-main">
        <Routes>
          <Route path="/" element={<TicketList key={refreshList ? 1 : 0} />} />
          <Route path="/tickets/:id" element={<TicketDetail />} />
          <Route path="/create" element={<TicketForm />} />
          <Route path="/edit/:id" element={<TicketForm isEdit={true} />} />
          <Route
            path="/import"
            element={
              <BulkImport
                onSuccess={() => {
                  setRefreshList(!refreshList);
                }}
              />
            }
          />
        </Routes>
      </main>

      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}
