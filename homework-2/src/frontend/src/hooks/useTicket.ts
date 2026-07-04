import { useState, useEffect } from "react";
import { Ticket } from "../types";
import { ticketApi } from "../api/client";

interface UseTicketResult {
  ticket: Ticket | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useTicket(id: string | undefined): UseTicketResult {
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [loading, setLoading] = useState(!!id);
  const [error, setError] = useState<string | null>(null);

  const refetch = async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const data = await ticketApi.getTicket(id);
      setTicket(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch ticket");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refetch();
  }, [id]);

  return { ticket, loading, error, refetch };
}
