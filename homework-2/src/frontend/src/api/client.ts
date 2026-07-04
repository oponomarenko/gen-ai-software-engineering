import {
  Ticket,
  TicketCreate,
  TicketUpdate,
  ImportSummary,
  ClassificationResult,
  Category,
  Priority,
  Status,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

export const ticketApi = {
  async createTicket(ticket: TicketCreate, autoClassify = false): Promise<Ticket> {
    const url = new URL(`${API_BASE_URL}/tickets`);
    if (autoClassify) {
      url.searchParams.set("auto_classify", "true");
    }

    const response = await fetch(url.toString(), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(ticket),
    });
    return handleResponse<Ticket>(response);
  },

  async listTickets(
    category?: Category,
    priority?: Priority,
    status?: Status
  ): Promise<Ticket[]> {
    const url = new URL(`${API_BASE_URL}/tickets`);
    if (category) url.searchParams.set("category", category);
    if (priority) url.searchParams.set("priority", priority);
    if (status) url.searchParams.set("status", status);

    const response = await fetch(url.toString());
    return handleResponse<Ticket[]>(response);
  },

  async getTicket(id: string): Promise<Ticket> {
    const response = await fetch(`${API_BASE_URL}/tickets/${id}`);
    return handleResponse<Ticket>(response);
  },

  async updateTicket(id: string, update: TicketUpdate): Promise<Ticket> {
    const response = await fetch(`${API_BASE_URL}/tickets/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(update),
    });
    return handleResponse<Ticket>(response);
  },

  async deleteTicket(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/tickets/${id}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
  },

  async autoClassifyTicket(id: string): Promise<ClassificationResult> {
    const response = await fetch(`${API_BASE_URL}/tickets/${id}/auto-classify`, {
      method: "POST",
    });
    return handleResponse<ClassificationResult>(response);
  },

  async importFile(file: File): Promise<ImportSummary> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/tickets/import`, {
      method: "POST",
      body: formData,
    });
    return handleResponse<ImportSummary>(response);
  },
};
