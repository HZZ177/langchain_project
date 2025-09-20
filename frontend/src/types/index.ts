// 用户相关类型
export interface User {
  id: number
  username: string
  email: string
  is_active: boolean
  is_admin: boolean
  created_at: string
  updated_at: string
}

export interface LoginForm {
  username: string
  password: string
}

export interface RegisterForm {
  username: string
  email: string
  password: string
}

export interface Token {
  access_token: string
  refresh_token: string
  token_type: string
}

// Agent相关类型
export interface Agent {
  id: number
  name: string
  type: string
  description: string
  is_system: boolean
  is_active: boolean
  created_by?: number
  created_at: string
  updated_at: string
}

// 会话相关类型
export interface Session {
  id: number
  user_id: number
  agent_id: number
  name: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Conversation {
  id: number
  session_id: number
  message_type: 'user' | 'assistant' | 'system'
  content: string
  extra_data?: Record<string, any>
  created_at: string
}

// WebSocket消息类型
export interface WebSocketMessage {
  type: string
  data: any
}

export interface UserMessage {
  type: 'user_message'
  data: {
    content: string
    extra_data?: Record<string, any>
  }
}

export interface AgentResponse {
  type: 'agent_response'
  data: {
    content: string
    is_final: boolean
    extra_data?: Record<string, any>
  }
}

export interface ErrorMessage {
  type: 'error'
  data: {
    code: string
    message: string
  }
}

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  code?: number
  timestamp?: string
}

export interface ApiError {
  success: false
  error: {
    code: string
    message: string
    details?: string
  }
  timestamp: string
}
