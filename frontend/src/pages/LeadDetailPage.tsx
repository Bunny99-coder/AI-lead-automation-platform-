import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../services/api";
import { AIAction, AutomationEvent, Lead } from "../types";

export function LeadDetailPage() {
  const { id } = useParams();
  const leadId = Number(id);
  const [lead, setLead] = useState<Lead | null>(null);
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [actions, setActions] = useState<AIAction[]>([]);
  const [events, setEvents] = useState<AutomationEvent[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!leadId) return;
    Promise.all([
      api.getLead(leadId),
      api.getConversation(leadId),
      api.getActions(leadId),
      api.getEvents(leadId),
    ])
      .then(([leadData, convo, actionsData, eventsData]) => {
        setLead(leadData);
        setMessages(convo.messages);
        setActions(actionsData.actions);
        setEvents(eventsData.events);
      })
      .catch((err) => setError(err.message));
  }, [leadId]);

  if (error) return <p>Error: {error}</p>;
  if (!lead) return <p>Loading lead...</p>;

  return (
    <div>
      <Link to="/">← Back to dashboard</Link>
      <h1>Lead #{lead.id}: {lead.name || "Unknown"}</h1>

      <div className="section card">
        <h2>Contact Information</h2>
        <p>Email: {lead.email || "-"}</p>
        <p>Phone: {lead.phone || "-"}</p>
        <p>GHL Contact ID: {lead.ghl_contact_id}</p>
        <p>Status: {lead.status}</p>
        <p>Qualification: {lead.qualification_status}</p>
        <p>Pipeline Stage: {lead.pipeline_stage || "-"}</p>
        <p>Appointment ID: {lead.appointment_id ?? "None"}</p>
      </div>

      <div className="section">
        <h2>Conversation History</h2>
        {messages.length === 0 ? (
          <p>No messages yet.</p>
        ) : (
          <ul>
            {messages.map((msg, idx) => (
              <li key={idx}>
                <strong>{msg.role}:</strong> {msg.content}
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="section">
        <h2>AI Actions</h2>
        <table>
          <thead>
            <tr>
              <th>Action</th>
              <th>Tool</th>
              <th>Success</th>
              <th>Error</th>
            </tr>
          </thead>
          <tbody>
            {actions.map((action) => (
              <tr key={action.id}>
                <td>{action.action_type}</td>
                <td>{action.tool_used || "-"}</td>
                <td>{action.success ? "Yes" : "No"}</td>
                <td>{action.error || "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="section">
        <h2>Automation Events</h2>
        <table>
          <thead>
            <tr>
              <th>Type</th>
              <th>Status</th>
              <th>Retries</th>
              <th>Error</th>
            </tr>
          </thead>
          <tbody>
            {events.map((event) => (
              <tr key={event.id}>
                <td>{event.event_type}</td>
                <td>{event.status}</td>
                <td>{event.retry_count}</td>
                <td>{event.error || "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
