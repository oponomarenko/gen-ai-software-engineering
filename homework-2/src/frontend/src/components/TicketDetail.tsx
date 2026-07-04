import { useParams, useNavigate } from "react-router-dom";
import { useState } from "react";
import { useTicket } from "../hooks/useTicket";
import { useToast } from "../hooks/useToast";
import { ticketApi } from "../api/client";
import "./TicketDetail.css";

export function TicketDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { ticket, loading, error, refetch } = useTicket(id);
  const { addToast } = useToast();
  const [classifying, setClassifying] = useState(false);

  const handleAutoClassify = async () => {
    if (!id) return;
    setClassifying(true);
    try {
      await ticketApi.autoClassifyTicket(id);
      addToast("Ticket auto-classified successfully!", "success");
      refetch();
    } catch (err) {
      addToast(err instanceof Error ? err.message : "Failed to classify", "error");
    } finally {
      setClassifying(false);
    }
  };

  const handleDelete = async () => {
    if (!id) return;
    if (!confirm("Are you sure you want to delete this ticket?")) return;

    try {
      await ticketApi.deleteTicket(id);
      addToast("Ticket deleted", "success");
      navigate("/");
    } catch (err) {
      addToast(err instanceof Error ? err.message : "Failed to delete", "error");
    }
  };

  if (loading) return <div className="loading">Loading ticket...</div>;
  if (error) return <div className="error-message">{error}</div>;
  if (!ticket) return <div className="error-message">Ticket not found</div>;

  return (
    <div className="ticket-detail-container">
      <button onClick={() => navigate("/")} className="btn btn-secondary back-btn">
        ← Back to List
      </button>

      <div className="ticket-detail-content">
        <div className="ticket-detail-header">
          <div>
            <h1>{ticket.subject}</h1>
            <p className="ticket-id">ID: {ticket.id}</p>
          </div>
          <div className="ticket-detail-actions">
            <button
              onClick={() => navigate(`/edit/${id}`)}
              className="btn btn-secondary"
            >
              Edit
            </button>
            <button onClick={handleDelete} className="btn btn-danger">
              Delete
            </button>
          </div>
        </div>

        <div className="ticket-detail-grid">
          <section className="detail-section">
            <h2>Customer Information</h2>
            <div className="detail-row">
              <label>Name:</label>
              <span>{ticket.customer_name}</span>
            </div>
            <div className="detail-row">
              <label>Email:</label>
              <span>{ticket.customer_email}</span>
            </div>
            <div className="detail-row">
              <label>Customer ID:</label>
              <span>{ticket.customer_id}</span>
            </div>
          </section>

          <section className="detail-section">
            <h2>Ticket Information</h2>
            <div className="detail-row">
              <label>Status:</label>
              <span className="status-badge">{ticket.status.replace(/_/g, " ")}</span>
            </div>
            <div className="detail-row">
              <label>Category:</label>
              <span className="category-badge">
                {ticket.category.replace(/_/g, " ")}
              </span>
            </div>
            <div className="detail-row">
              <label>Priority:</label>
              <span className="priority-badge">{ticket.priority}</span>
            </div>
            <div className="detail-row">
              <label>Assigned To:</label>
              <span>{ticket.assigned_to || "Unassigned"}</span>
            </div>
          </section>

          <section className="detail-section full-width">
            <h2>Description</h2>
            <p className="description-text">{ticket.description}</p>
          </section>

          {ticket.classification && (
            <section className="detail-section full-width">
              <h2>Classification Result</h2>
              <div className="detail-row">
                <label>Category:</label>
                <span>{ticket.classification.category.replace(/_/g, " ")}</span>
              </div>
              <div className="detail-row">
                <label>Priority:</label>
                <span>{ticket.classification.priority}</span>
              </div>
              <div className="detail-row">
                <label>Confidence:</label>
                <span>
                  {(ticket.classification.confidence * 100).toFixed(1)}%
                </span>
              </div>
              <div className="detail-row">
                <label>Reasoning:</label>
                <span>{ticket.classification.reasoning}</span>
              </div>
              <div className="detail-row">
                <label>Keywords Found:</label>
                <span>
                  {ticket.classification.keywords_found.length > 0
                    ? ticket.classification.keywords_found.join(", ")
                    : "None"}
                </span>
              </div>
              <div className="detail-row">
                <label>Manual Override:</label>
                <span>{ticket.classification.manual_override ? "Yes" : "No"}</span>
              </div>
            </section>
          )}

          {ticket.metadata && (
            <section className="detail-section">
              <h2>Metadata</h2>
              <div className="detail-row">
                <label>Source:</label>
                <span>{ticket.metadata.source.replace(/_/g, " ")}</span>
              </div>
              {ticket.metadata.browser && (
                <div className="detail-row">
                  <label>Browser:</label>
                  <span>{ticket.metadata.browser}</span>
                </div>
              )}
              {ticket.metadata.device_type && (
                <div className="detail-row">
                  <label>Device Type:</label>
                  <span>{ticket.metadata.device_type}</span>
                </div>
              )}
            </section>
          )}

          <section className="detail-section">
            <h2>Dates</h2>
            <div className="detail-row">
              <label>Created:</label>
              <span>{new Date(ticket.created_at).toLocaleString()}</span>
            </div>
            <div className="detail-row">
              <label>Updated:</label>
              <span>{new Date(ticket.updated_at).toLocaleString()}</span>
            </div>
            {ticket.resolved_at && (
              <div className="detail-row">
                <label>Resolved:</label>
                <span>{new Date(ticket.resolved_at).toLocaleString()}</span>
              </div>
            )}
          </section>

          {ticket.tags.length > 0 && (
            <section className="detail-section full-width">
              <h2>Tags</h2>
              <div className="tags-list">
                {ticket.tags.map((tag) => (
                  <span key={tag} className="tag">
                    {tag}
                  </span>
                ))}
              </div>
            </section>
          )}

          <section className="detail-section full-width">
            <button
              onClick={handleAutoClassify}
              className="btn btn-primary"
              disabled={classifying}
            >
              {classifying ? "Classifying..." : "Auto-classify"}
            </button>
          </section>
        </div>
      </div>
    </div>
  );
}
