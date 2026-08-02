const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

export const api = {
  getStats: () => fetchJson<import("../types").DashboardStats>("/admin/stats"),
  getLeads: () => fetchJson<import("../types").LeadListResponse>("/leads"),
  getLead: (id: number) => fetchJson<import("../types").Lead>(`/leads/${id}`),
  getConversation: (id: number) => fetchJson<{ messages: { role: string; content: string }[] }>(`/leads/${id}/conversation`),
  getActions: (id: number) => fetchJson<{ actions: import("../types").AIAction[] }>(`/leads/${id}/actions`),
  getEvents: (id: number) => fetchJson<{ events: import("../types").AutomationEvent[] }>(`/leads/${id}/events`),
  getRecentActions: () => fetchJson<{ items: import("../types").AIAction[] }>("/admin/actions"),
  getRecentWebhooks: () => fetchJson<{ items: import("../types").WebhookEvent[] }>("/admin/webhooks"),
};
