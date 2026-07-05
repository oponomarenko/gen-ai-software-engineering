import { useState } from "react";
import { Link } from "react-router-dom";
import { Category, Priority, Status } from "../types";
import { useTickets } from "../hooks/useTickets";
import "./TicketList.css";

export function TicketList() {
  const [selectedCategory, setSelectedCategory] = useState<Category | undefined>();
  const [selectedPriority, setSelectedPriority] = useState<Priority | undefined>();
  const [selectedStatus, setSelectedStatus] = useState<Status | undefined>();

  const { tickets, loading, error, refetch } = useTickets(
    selectedCategory,
    selectedPriority,
    selectedStatus
  );

  const categoryOptions = Object.values(Category);
  const priorityOptions = Object.values(Priority);
  const statusOptions = Object.values(Status);

  const getPriorityColor = (priority: Priority) => {
    switch (priority) {
      case Priority.urgent:
        return "#d32f2f";
      case Priority.high:
        return "#f57c00";
      case Priority.medium:
        return "#fbc02d";
      case Priority.low:
        return "#388e3c";
    }
  };

  return (
    <div className="ticket-list-container">
      <div className="ticket-list-header">
        <h1>Support Tickets</h1>
        <Link to="/create" className="btn btn-primary">
          + New Ticket
        </Link>
      </div>

      <div className="filters">
        <select
          value={selectedCategory || ""}
          onChange={(e) =>
            setSelectedCategory(e.target.value ? (e.target.value as Category) : undefined)
          }
          className="filter-select"
        >
          <option value="">All Categories</option>
          {categoryOptions.map((cat) => (
            <option key={cat} value={cat}>
              {cat.replace(/_/g, " ")}
            </option>
          ))}
        </select>

        <select
          value={selectedPriority || ""}
          onChange={(e) =>
            setSelectedPriority(e.target.value ? (e.target.value as Priority) : undefined)
          }
          className="filter-select"
        >
          <option value="">All Priorities</option>
          {priorityOptions.map((pri) => (
            <option key={pri} value={pri}>
              {pri.charAt(0).toUpperCase() + pri.slice(1)}
            </option>
          ))}
        </select>

        <select
          value={selectedStatus || ""}
          onChange={(e) =>
            setSelectedStatus(e.target.value ? (e.target.value as Status) : undefined)
          }
          className="filter-select"
        >
          <option value="">All Statuses</option>
          {statusOptions.map((stat) => (
            <option key={stat} value={stat}>
              {stat.replace(/_/g, " ")}
            </option>
          ))}
        </select>

        <button onClick={refetch} className="btn btn-secondary" disabled={loading}>
          Refresh
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading">Loading tickets...</div>
      ) : tickets.length === 0 ? (
        <div className="no-tickets">No tickets found</div>
      ) : (
        <div className="tickets-grid">
          {tickets.map((ticket) => (
            <Link
              key={ticket.id}
              to={`/tickets/${ticket.id}`}
              className="ticket-card"
            >
              <div className="ticket-card-header">
                <h3>{ticket.subject}</h3>
                <span
                  className="priority-badge"
                  style={{ backgroundColor: getPriorityColor(ticket.priority) }}
                >
                  {ticket.priority}
                </span>
              </div>
              <p className="ticket-customer">
                {ticket.customer_name} ({ticket.customer_email})
              </p>
              <p className="ticket-description">{ticket.description.substring(0, 100)}...</p>
              <div className="ticket-card-footer">
                <span className="category-badge">
                  {ticket.category.replace(/_/g, " ")}
                </span>
                <span className="status-badge">
                  {ticket.status.replace(/_/g, " ")}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
