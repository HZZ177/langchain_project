import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Session, Conversation, Agent } from '@/types'
import { sessionService } from '@/services/session'
import { agentService } from '@/services/agent'
import { websocketService } from '@/services/websocket'

export const useChatStore = defineStore('chat', () => {
  // 状态
  const sessions = ref<Session[]>([])
  const currentSession = ref<Session | null>(null)
  const conversations = ref<Conversation[]>([])
  const agents = ref<Agent[]>([])
  const currentAgentId = ref<number | null>(null)
  const loading = ref(false)
  const wsConnected = ref(false)
  const streamingMessage = ref('')
  const isStreaming = ref(false)
  const isWaitingForResponse = ref(false)

  // 计算属性
  const currentAgent = computed(() => {
    if (!currentAgentId.value) return null
    return agents.value.find(agent => agent.id === currentAgentId.value) || null
  })

  const filteredSessions = computed(() => {
    if (!currentAgentId.value) return []
    return sessions.value.filter(session => session.agent_id === currentAgentId.value)
  })

  const sortedSessions = computed(() => {
    return [...filteredSessions.value].sort((a, b) =>
      new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    )
  })

  // 获取Agent列表
  const fetchAgents = async () => {
    try {
      agents.value = await agentService.getAgents()
      // 如果没有选中的Agent且有可用Agent，选择第一个
      if (!currentAgentId.value && agents.value.length > 0) {
        currentAgentId.value = agents.value[0].id
      }
    } catch (error) {
      console.error('获取Agent列表失败:', error)
    }
  }

  // 获取会话列表
  const fetchSessions = async () => {
    try {
      sessions.value = await sessionService.getSessions()
    } catch (error) {
      console.error('获取会话列表失败:', error)
    }
  }

  // 设置当前Agent
  const setCurrentAgent = (agentId: number) => {
    currentAgentId.value = agentId
    // 切换Agent时清除当前会话
    if (currentSession.value && currentSession.value.agent_id !== agentId) {
      currentSession.value = null
      conversations.value = []
      if (wsConnected.value) {
        websocketService.disconnect()
        wsConnected.value = false
      }
    }
  }

  // 创建新会话（在当前Agent下）
  const createSession = async (name?: string) => {
    if (!currentAgentId.value) {
      throw new Error('请先选择一个Agent')
    }

    try {
      const newSession = await sessionService.createSession(currentAgentId.value, name || '新对话')
      sessions.value.unshift(newSession)
      return newSession
    } catch (error) {
      console.error('创建会话失败:', error)
      throw error
    }
  }

  // 设置当前会话
  const setCurrentSession = async (session: Session) => {
    // 断开之前的WebSocket连接
    if (wsConnected.value) {
      websocketService.disconnect()
      wsConnected.value = false
    }

    currentSession.value = session
    
    // 获取对话历史
    await fetchConversations(session.id)
    
    // 建立WebSocket连接
    await connectWebSocket(session.id)
  }

  // 获取对话历史
  const fetchConversations = async (sessionId: number) => {
    try {
      conversations.value = await sessionService.getSessionConversations(sessionId)
    } catch (error) {
      console.error('获取对话历史失败:', error)
    }
  }

  // 建立WebSocket连接
  const connectWebSocket = async (sessionId: number) => {
    const authStore = useAuthStore()
    if (!authStore.token) return

    try {
      await websocketService.connect(sessionId.toString(), authStore.token)
      wsConnected.value = true

      // 设置消息处理器
      websocketService.onMessage('agent_response', (data) => {
        // 收到第一个响应时，清除等待状态
        if (isWaitingForResponse.value) {
          isWaitingForResponse.value = false
        }

        if (data.is_final) {
          // 最终响应，添加到对话历史
          if (streamingMessage.value) {
            conversations.value.push({
              id: Date.now(), // 临时ID
              session_id: sessionId,
              message_type: 'assistant',
              content: streamingMessage.value,
              extra_data: data.extra_data,
              created_at: new Date().toISOString(),
            })
            streamingMessage.value = ''
          }
          isStreaming.value = false
        } else {
          // 流式响应
          streamingMessage.value += data.content
          isStreaming.value = true
        }
      })

      websocketService.onMessage('error', (data) => {
        console.error('WebSocket错误:', data)
        isStreaming.value = false
        isWaitingForResponse.value = false
        streamingMessage.value = ''
      })

    } catch (error) {
      console.error('WebSocket连接失败:', error)
    }
  }

  // 发送消息
  const sendMessage = async (content: string) => {
    if (!currentSession.value || !wsConnected.value) {
      throw new Error('未连接到会话')
    }

    // 添加用户消息到对话历史
    const userMessage: Conversation = {
      id: Date.now(), // 临时ID
      session_id: currentSession.value.id,
      message_type: 'user',
      content,
      created_at: new Date().toISOString(),
    }
    conversations.value.push(userMessage)

    // 设置等待响应状态
    isWaitingForResponse.value = true
    streamingMessage.value = ''
    isStreaming.value = false

    // 发送WebSocket消息
    websocketService.sendUserMessage(content)
  }

  // 更新会话名称
  const updateSessionName = async (sessionId: number, name: string) => {
    try {
      const updatedSession = await sessionService.updateSession(sessionId, { name })
      const index = sessions.value.findIndex(s => s.id === sessionId)
      if (index !== -1) {
        sessions.value[index] = updatedSession
      }
      if (currentSession.value?.id === sessionId) {
        currentSession.value = updatedSession
      }
    } catch (error) {
      console.error('更新会话名称失败:', error)
      throw error
    }
  }

  // 删除会话
  const deleteSession = async (sessionId: number) => {
    try {
      await sessionService.deleteSession(sessionId)
      sessions.value = sessions.value.filter(s => s.id !== sessionId)
      
      if (currentSession.value?.id === sessionId) {
        currentSession.value = null
        conversations.value = []
        if (wsConnected.value) {
          websocketService.disconnect()
          wsConnected.value = false
        }
      }
    } catch (error) {
      console.error('删除会话失败:', error)
      throw error
    }
  }

  // 清空对话历史
  const clearConversations = async () => {
    if (!currentSession.value) return

    try {
      await sessionService.clearSessionConversations(currentSession.value.id)
      conversations.value = []
    } catch (error) {
      console.error('清空对话历史失败:', error)
      throw error
    }
  }

  // 断开WebSocket连接
  const disconnectWebSocket = () => {
    if (wsConnected.value) {
      websocketService.disconnect()
      wsConnected.value = false
    }
  }

  return {
    // 状态
    sessions,
    currentSession,
    conversations,
    agents,
    currentAgentId,
    loading,
    wsConnected,
    streamingMessage,
    isStreaming,
    isWaitingForResponse,

    // 计算属性
    currentAgent,
    filteredSessions,
    sortedSessions,

    // 方法
    fetchAgents,
    fetchSessions,
    setCurrentAgent,
    createSession,
    setCurrentSession,
    fetchConversations,
    connectWebSocket,
    sendMessage,
    updateSessionName,
    deleteSession,
    clearConversations,
    disconnectWebSocket,
  }
})

// 导入useAuthStore（避免循环依赖）
import { useAuthStore } from './auth'
