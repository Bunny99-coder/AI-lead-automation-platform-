import { useEffect, useState } from "react";
import { StatsCards } from "../components/StatsCards";
import { LeadsTable } from "../components/LeadsTable";
import { api } from "../services/api";
import { AIAction, DashboardStats, Lead, WebhookEvent } from "../types";

export function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [actions, setActions] = useState<AIAction[]>([]);
  const [webhooks, setWebhooks] = useState<WebhookEvent[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      api.getStats(),
      api.getLeads(),
      api.getRecentActions(),
      api.getRecentWebhooks(),
    ])
      .then(([statsData, leadsData, actionsData, webhooksData]) => {
        setStats(statsData);
        setLeads(leadsData.items);
        setActions(actionsData.items);
        setWebhooks(webhooksData.items);
      })
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <p>Error: {error}</p>;

  return (
    <div>
      <h1>AI Lead Automation Dashboard</h1>
      <StatsCards stats={stats} />

      <div className="section">
        <h2>Recent Leads</h2>
        <LeadsTable leads={leads} />
      </div>

      <div className="section">
        <h2>Recent AI Actions</h2>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Lead</th>
              <th>Action</th>
              <th>Tool</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {actions.map((action) => (
              <tr key={action.id}>
                <td>{action.id}</td>
                <td>{action.lead_id ?? "-"}</td>
                <td>{action.action_type}</td>
                <td>{action.tool_used || "-"}</td>
                <td>
                  <span className={`badge ${action.success ? "success" : "failed"}`}>
                    {action.success ? "success" : "failed"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="section">
        <h2>Recent Webhook Events</h2>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Source</th>
              <th>Type</th>
              <th>Status</th>
              <th>Lead</th>
            </tr>
          </thead>
          <tbody>
            {webhooks.map((event) => (
              <tr key={event.id}>
                <td>{event.id}</td>
                <td>{event.source}</td>
                <td>{event.event_type}</td>
                <td>{event.status}</td>
                <td>{event.lead_id ?? "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
