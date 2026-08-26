import type { DocumentSource } from './document'
import type { QueryScope } from './search'

export type AgentActivityStatus = 'pending' | 'in_progress' | 'done'

export interface AgentActivity {
  id: string
  label: string
  status: AgentActivityStatus
}

export interface AgentTask {
  id: string
  scope: QueryScope
  activities: AgentActivity[]
}

export type AgentMessageRole = 'user' | 'agent'

export interface AgentMessage {
  id: string
  role: AgentMessageRole
  text: string
  createdAt: string
  activities?: AgentActivity[]
  sources?: DocumentSource[]
}

export interface AgentQueryRequest {
  question: string
  scope: QueryScope
  history: AgentMessage[]
}

export interface AgentResponse {
  message: AgentMessage
}
