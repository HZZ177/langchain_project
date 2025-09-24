import api from './api'

export interface TitleGenerationConfig {
  enabled: boolean
  model: string
  api_key: string
  base_url: string
  temperature: number
  max_tokens: number | null
  trigger_rounds: number
}

export const systemService = {
  // 获取标题生成配置
  async getTitleGenerationConfig(): Promise<TitleGenerationConfig> {
    const response = await api.get('/system/config/title-generation')
    return response.data
  },

  // 更新标题生成配置
  async updateTitleGenerationConfig(config: TitleGenerationConfig): Promise<void> {
    await api.put('/system/config/title-generation', config)
  },

  // 获取所有系统配置
  async getAllSystemConfigs(): Promise<Record<string, any>> {
    const response = await api.get('/system/config')
    return response.data.configs
  },

  // 批量更新系统配置
  async updateSystemConfigs(configs: Record<string, any>): Promise<void> {
    await api.put('/system/config', configs)
  }
}
