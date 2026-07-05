import { useState, useEffect } from "react";
import { Ticket, Category, Priority, Status } from "../types";
import { ticketApi } from "../api/client";

interface UseTicketsResult {
  tickets: Ticket[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useTickets(
  category?: Category,
  priority?: Priority,
  status?: Status
): UseTicketsResult {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refetch = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await ticketApi.listTickets(category, priority, status);
      setTickets(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch tickets");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refetch();
  }, [category, priority, status]);

  return { tickets, loading, error, refetch };
}
