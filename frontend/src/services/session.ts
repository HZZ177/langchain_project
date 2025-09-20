import api from './api'
import type { Session, Conversation } from '@/types'

export const sessionService = {
  // 获取用户会话列表
  async getSessions(): Promise<Session[]> {
    const response = await api.get('/sessions/')
    return response.data
  },

  // 创建新会话
  async createSession(agentId: number, name: string = '新对话'): Promise<Session> {
    const response = await api.post('/sessions/', {
      agent_id: agentId,
      name,
    })
    return response.data
  },

  // 获取会话详情
  async getSession(sessionId: number): Promise<Session> {
    const response = await api.get(`/sessions/${sessionId}`)
    return response.data
  },

  // 更新会话
  async updateSession(sessionId: number, data: { name?: string; is_active?: boolean }): Promise<Session> {
    const response = await api.put(`/sessions/${sessionId}`, data)
    return response.data
  },

  // 删除会话
  async deleteSession(sessionId: number): Promise<void> {
    await api.delete(`/sessions/${sessionId}`)
  },

  // 获取会话对话历史
  async getSessionConversations(sessionId: number, limit: number = 100): Promise<Conversation[]> {
    const response = await api.get(`/sessions/${sessionId}/conversations`, {
      params: { limit },
    })
    return response.data
  },

  // 清空会话对话历史
  async clearSessionConversations(sessionId: number): Promise<void> {
    await api.delete(`/sessions/${sessionId}/conversations`)
  },
}
