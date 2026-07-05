import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { TicketCreate, TicketUpdate, Category, Priority } from "../types";
import { useTicket } from "../hooks/useTicket";
import { useToast } from "../hooks/useToast";
import { ticketApi } from "../api/client";
import "./TicketForm.css";

interface TicketFormProps {
  isEdit?: boolean;
}

export function TicketForm({ isEdit = false }: TicketFormProps) {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { addToast } = useToast();
  const { ticket, loading } = useTicket(isEdit ? id : undefined);

  const [formData, setFormData] = useState<TicketCreate>({
    customer_id: "",
    customer_email: "",
    customer_name: "",
    subject: "",
    description: "",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (ticket && isEdit) {
      setFormData({
        customer_id: ticket.customer_id,
        customer_email: ticket.customer_email,
        customer_name: ticket.customer_name,
        subject: ticket.subject,
        description: ticket.description,
        category: ticket.category,
        priority: ticket.priority,
        status: ticket.status,
        tags: ticket.tags,
        metadata: ticket.metadata,
      });
    }
  }, [ticket, isEdit]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.customer_id.trim()) newErrors.customer_id = "Customer ID is required";
    if (!formData.customer_email.trim()) newErrors.customer_email = "Email is required";
    if (formData.customer_email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.customer_email)) {
      newErrors.customer_email = "Invalid email format";
    }
    if (!formData.customer_name.trim()) newErrors.customer_name = "Customer name is required";
    if (!formData.subject.trim()) newErrors.subject = "Subject is required";
    if (formData.subject && formData.subject.length > 200) {
      newErrors.subject = "Subject must be 200 characters or less";
    }
    if (!formData.description.trim()) newErrors.description = "Description is required";
    if (formData.description && formData.description.length < 10) {
      newErrors.description = "Description must be at least 10 characters";
    }
    if (formData.description && formData.description.length > 2000) {
      newErrors.description = "Description must be 2000 characters or less";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      addToast("Please fix the errors in the form", "error");
      return;
    }

    setSubmitting(true);
    try {
      if (isEdit && id) {
        const updateData: TicketUpdate = {
          customer_id: formData.customer_id,
          customer_email: formData.customer_email,
          customer_name: formData.customer_name,
          subject: formData.subject,
          description: formData.description,
          category: formData.category,
          priority: formData.priority,
          tags: formData.tags,
        };
        await ticketApi.updateTicket(id, updateData);
        addToast("Ticket updated successfully!", "success");
        navigate(`/tickets/${id}`);
      } else {
        const created = await ticketApi.createTicket(formData);
        addToast("Ticket created successfully!", "success");
        navigate(`/tickets/${created.id}`);
      }
    } catch (err) {
      addToast(err instanceof Error ? err.message : "Failed to save ticket", "error");
    } finally {
      setSubmitting(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  if (loading) return <div className="loading">Loading ticket...</div>;

  return (
    <div className="ticket-form-container">
      <button onClick={() => navigate("/")} className="btn btn-secondary back-btn">
        ← Back to List
      </button>

      <form onSubmit={handleSubmit} className="ticket-form">
        <h1>{isEdit ? "Edit Ticket" : "Create New Ticket"}</h1>

        <fieldset className="form-section">
          <legend>Customer Information</legend>

          <div className="form-group">
            <label htmlFor="customer_id">Customer ID *</label>
            <input
              id="customer_id"
              type="text"
              name="customer_id"
              value={formData.customer_id}
              onChange={handleChange}
              className={errors.customer_id ? "form-input error" : "form-input"}
              maxLength={100}
            />
            {errors.customer_id && <span className="error-text">{errors.customer_id}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="customer_email">Email *</label>
            <input
              id="customer_email"
              type="email"
              name="customer_email"
              value={formData.customer_email}
              onChange={handleChange}
              className={errors.customer_email ? "form-input error" : "form-input"}
            />
            {errors.customer_email && (
              <span className="error-text">{errors.customer_email}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="customer_name">Customer Name *</label>
            <input
              id="customer_name"
              type="text"
              name="customer_name"
              value={formData.customer_name}
              onChange={handleChange}
              className={errors.customer_name ? "form-input error" : "form-input"}
              maxLength={200}
            />
            {errors.customer_name && (
              <span className="error-text">{errors.customer_name}</span>
            )}
          </div>
        </fieldset>

        <fieldset className="form-section">
          <legend>Ticket Details</legend>

          <div className="form-group">
            <label htmlFor="subject">Subject *</label>
            <input
              id="subject"
              type="text"
              name="subject"
              value={formData.subject}
              onChange={handleChange}
              className={errors.subject ? "form-input error" : "form-input"}
              maxLength={200}
            />
            {errors.subject && <span className="error-text">{errors.subject}</span>}
            <span className="char-count">
              {formData.subject.length}/200
            </span>
          </div>

          <div className="form-group">
            <label htmlFor="description">Description *</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              className={errors.description ? "form-input error" : "form-input"}
              rows={6}
              maxLength={2000}
            />
            {errors.description && (
              <span className="error-text">{errors.description}</span>
            )}
            <span className="char-count">
              {formData.description.length}/2000
            </span>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="category">Category</label>
              <select
                id="category"
                name="category"
                value={formData.category || Category.other}
                onChange={handleChange}
                className="form-input"
              >
                {Object.values(Category).map((cat) => (
                  <option key={cat} value={cat}>
                    {cat.replace(/_/g, " ")}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="priority">Priority</label>
              <select
                id="priority"
                name="priority"
                value={formData.priority || Priority.medium}
                onChange={handleChange}
                className="form-input"
              >
                {Object.values(Priority).map((pri) => (
                  <option key={pri} value={pri}>
                    {pri.charAt(0).toUpperCase() + pri.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </fieldset>

        <div className="form-actions">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={submitting}
          >
            {submitting ? "Saving..." : isEdit ? "Update Ticket" : "Create Ticket"}
          </button>
          <button
            type="button"
            onClick={() => navigate("/")}
            className="btn btn-secondary"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
