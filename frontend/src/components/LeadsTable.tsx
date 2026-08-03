import { Link } from "react-router-dom";
import { Lead } from "../types";

interface Props {
  leads: Lead[];
}

export function LeadsTable({ leads }: Props) {
  return (
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Email</th>
          <th>Status</th>
          <th>Qualification</th>
          <th>Pipeline</th>
        </tr>
      </thead>
      <tbody>
        {leads.map((lead) => (
          <tr key={lead.id}>
            <td><Link to={`/leads/${lead.id}`}>{lead.id}</Link></td>
            <td>{lead.name || "-"}</td>
            <td>{lead.email || "-"}</td>
            <td>{lead.status}</td>
            <td>{lead.qualification_status}</td>
            <td>{lead.pipeline_stage || "-"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
