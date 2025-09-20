import api from './api'
import type { Agent } from '@/types'

export const agentService = {
  // 获取Agent列表
  async getAgents(): Promise<Agent[]> {
    const response = await api.get('/agents/')
    return response.data
  },

  // 获取Agent详情
  async getAgent(agentId: number): Promise<Agent> {
    const response = await api.get(`/agents/${agentId}`)
    return response.data
  },

  // 获取Agent配置
  async getAgentConfig(agentId: number): Promise<Record<string, any>> {
    const response = await api.get(`/agents/${agentId}/config`)
    return response.data.config
  },

  // 获取Agent配置模式
  async getAgentConfigSchema(agentId: number): Promise<{
    schema: Record<string, any>
    supported_features: string[]
  }> {
    const response = await api.get(`/agents/${agentId}/config-schema`)
    return response.data
  },

  // 更新Agent配置
  async updateAgentConfig(agentId: number, config: Record<string, any>): Promise<void> {
    await api.put(`/agents/${agentId}/config`, config)
  },

  // 获取可用的Agent类型
  async getAvailableAgentTypes(): Promise<Record<string, any>> {
    const response = await api.get('/agents/types/available')
    return response.data.agent_types
  },
}
