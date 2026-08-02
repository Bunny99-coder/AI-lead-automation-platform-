import { DashboardStats } from "../types";

interface Props {
  stats: DashboardStats | null;
}

export function StatsCards({ stats }: Props) {
  if (!stats) return <p>Loading stats...</p>;

  const cards = [
    { label: "Total Leads", value: stats.total_leads },
    { label: "Qualified", value: stats.qualified_leads },
    { label: "Unqualified", value: stats.unqualified_leads },
    { label: "Appointments", value: stats.appointments },
    { label: "Active Follow-ups", value: stats.active_follow_ups },
    { label: "Failed Automations", value: stats.failed_automations },
  ];

  return (
    <div className="card-grid">
      {cards.map((card) => (
        <div className="card" key={card.label}>
          <h3>{card.label}</h3>
          <p>{card.value}</p>
        </div>
      ))}
    </div>
  );
}
