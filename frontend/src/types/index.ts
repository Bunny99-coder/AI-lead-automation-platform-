export interface Lead {
  id: number;
  ghl_contact_id: string;
  name: string | null;
  email: string | null;
  phone: string | null;
  status: string;
  qualification_status: string;
  pipeline_stage: string | null;
  appointment_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface LeadListResponse {
  items: Lead[];
  total: number;
}

export interface DashboardStats {
  total_leads: number;
  qualified_leads: number;
  unqualified_leads: number;
  appointments: number;
  active_follow_ups: number;
  failed_automations: number;
}

export interface AIAction {
  id: number;
  lead_id?: number;
  action_type: string;
  tool_used: string | null;
  success: boolean;
  error?: string | null;
  created_at: string;
}

export interface AutomationEvent {
  id: number;
  event_type: string;
  status: string;
  error: string | null;
  retry_count: number;
  created_at: string;
}

export interface WebhookEvent {
  id: number;
  source: string;
  event_type: string;
  status: string;
  lead_id: number | null;
  created_at: string;
}
