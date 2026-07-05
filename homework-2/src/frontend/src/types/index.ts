export enum Category {
  account_access = "account_access",
  technical_issue = "technical_issue",
  billing_question = "billing_question",
  feature_request = "feature_request",
  bug_report = "bug_report",
  other = "other",
}

export enum Priority {
  urgent = "urgent",
  high = "high",
  medium = "medium",
  low = "low",
}

export enum Status {
  new = "new",
  in_progress = "in_progress",
  waiting_customer = "waiting_customer",
  resolved = "resolved",
  closed = "closed",
}

export enum Source {
  web_form = "web_form",
  email = "email",
  api = "api",
  chat = "chat",
  phone = "phone",
}

export enum DeviceType {
  desktop = "desktop",
  mobile = "mobile",
  tablet = "tablet",
}

export interface TicketMetadata {
  source: Source;
  browser?: string | null;
  device_type?: DeviceType | null;
}

export interface ClassificationResult {
  category: Category;
  priority: Priority;
  confidence: number;
  reasoning: string;
  keywords_found: string[];
  manual_override: boolean;
}

export interface Ticket {
  id: string;
  customer_id: string;
  customer_email: string;
  customer_name: string;
  subject: string;
  description: string;
  category: Category;
  priority: Priority;
  status: Status;
  created_at: string;
  updated_at: string;
  resolved_at?: string | null;
  assigned_to?: string | null;
  tags: string[];
  metadata: TicketMetadata;
  classification?: ClassificationResult | null;
}

export interface TicketCreate {
  customer_id: string;
  customer_email: string;
  customer_name: string;
  subject: string;
  description: string;
  category?: Category;
  priority?: Priority;
  status?: Status;
  assigned_to?: string | null;
  tags?: string[];
  metadata?: TicketMetadata;
}

export interface TicketUpdate {
  customer_id?: string | null;
  customer_email?: string | null;
  customer_name?: string | null;
  subject?: string | null;
  description?: string | null;
  category?: Category | null;
  priority?: Priority | null;
  status?: Status | null;
  assigned_to?: string | null;
  tags?: string[] | null;
  metadata?: TicketMetadata | null;
}

export interface ImportRecordError {
  record_index: number;
  identifier?: string | null;
  message: string;
}

export interface ImportSummary {
  total: number;
  successful: number;
  failed: number;
  errors: ImportRecordError[];
  created_ticket_ids: string[];
}
