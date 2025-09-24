import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Session, Conversation, Agent, TemporarySession } from '@/types'
import { sessionService } from '@/services/session'
import { agentService } from '@/services/agent'
import { websocketService } from '@/services/websocket'

// 双模型头脑风暴相关类型
interface DiscussionConfig {
  model_a?: string
  model_b?: string
  style?: 'collaborative' | 'debate'
  max_rounds?: number
}

interface DiscussionRound {
  round: number
  modelA: {
    content: string
    isStreaming?: boolean
    isComplete?: boolean
  }
  modelB: {
    content: string
    isStreaming?: boolean
    isComplete?: boolean
  }
}

interface BrainstormSession {
  topic: string
  config?: DiscussionConfig
  rounds: DiscussionRound[]
  summary?: string
  isComplete: boolean
}

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
  const streamingMetadata = ref<any>(null)
  const isStreaming = ref(false)
  const isWaitingForResponse = ref(false)

  // 新增：临时会话管理
  let tempSessionIdCounter = -1 // 临时会话使用负数ID

  // 双模型头脑风暴相关状态
  const brainstormSession = ref<BrainstormSession | null>(null)
  const brainstormHistory = ref<BrainstormSession[]>([])  // 历史讨论记录
  const currentRound = ref(0)
  const currentSpeaker = ref<'model_a' | 'model_b' | null>(null)

  // 计算属性
  const currentAgent = computed(() => {
    if (!currentAgentId.value) return null
    return agents.value.find(agent => agent.id === currentAgentId.value) || null
  })

  const filteredSessions = computed(() => {
    if (!currentAgentId.value) return []
    // 只返回正式会话，不包含临时会话
    return sessions.value.filter(session =>
      session.agent_id === currentAgentId.value && !session.isTemporary
    )
  })

  const sortedSessions = computed(() => {
    return [...filteredSessions.value].sort((a, b) =>
      new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    )
  })

  // 新增：检查是否有可用的聊天界面（临时会话或正式会话）
  const hasActiveChat = computed(() => {
    return currentSession.value !== null
  })

  // 获取Agent列表
  const fetchAgents = async () => {
    try {
      agents.value = await agentService.getAgents()
      // 如果没有选中的Agent且有可用Agent，选择第一个并自动创建临时会话
      if (!currentAgentId.value && agents.value.length > 0) {
        await setCurrentAgent(agents.value[0].id)
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

  // 创建临时会话
  const createTemporarySession = (agentId: number): TemporarySession => {
    const now = new Date().toISOString()
    const tempSession: TemporarySession = {
      id: tempSessionIdCounter--,
      user_id: 0, // 临时会话暂不需要真实用户ID
      agent_id: agentId,
      name: '新对话',
      is_active: true,
      created_at: now,
      updated_at: now,
      isTemporary: true
    }
    return tempSession
  }

  // 清理临时会话
  const clearTemporarySession = () => {
    if (currentSession.value?.isTemporary) {
      currentSession.value = null
      conversations.value = []
      if (wsConnected.value) {
        websocketService.disconnect()
        wsConnected.value = false
      }
    }
  }

  // 将临时会话转为正式会话
  const convertTemporaryToRealSession = async (tempSession: TemporarySession): Promise<Session> => {
    try {
      const realSession = await sessionService.createSession(tempSession.agent_id, tempSession.name)

      // 更新会话列表
      sessions.value.unshift(realSession)

      // 更新当前会话
      currentSession.value = realSession

      return realSession
    } catch (error) {
      console.error('转换临时会话失败:', error)
      throw error
    }
  }

  // 设置当前Agent
  const setCurrentAgent = async (agentId: number) => {
    // 如果切换到不同的Agent，清理当前状态
    if (currentAgentId.value !== agentId) {
      // 清理临时会话
      clearTemporarySession()

      // 如果当前有正式会话且不属于新Agent，也清理
      if (currentSession.value && !currentSession.value.isTemporary && currentSession.value.agent_id !== agentId) {
        currentSession.value = null
        conversations.value = []
        if (wsConnected.value) {
          websocketService.disconnect()
          wsConnected.value = false
        }
      }
    }

    currentAgentId.value = agentId

    // 自动创建临时会话并设置为当前会话
    if (!currentSession.value) {
      const tempSession = createTemporarySession(agentId)
      currentSession.value = tempSession
      conversations.value = []
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
    // 如果点击的是当前会话，不执行任何操作
    if (currentSession.value?.id === session.id) {
      return
    }

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

      // 如果是头脑风暴Agent，尝试恢复头脑风暴会话
      if (currentAgent.value?.type === 'brainstorm_agent') {
        // 重置头脑风暴状态
        brainstormSession.value = null
        brainstormHistory.value = []
        currentRound.value = 0
        currentSpeaker.value = null

        // 获取所有头脑风暴记录
        const brainstormConversations = conversations.value.filter(
          conv => conv.message_type === 'assistant' && conv.extra_data?.type === 'brainstorm_session'
        )

        if (brainstormConversations.length > 0) {
          try {
            // 按时间排序，最新的在前
            const sortedConversations = brainstormConversations.sort((a, b) =>
              new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
            )

            // 解析所有讨论记录
            const allSessions: BrainstormSession[] = []
            for (const conv of sortedConversations) {
              try {
                const sessionData = JSON.parse(conv.content)
                allSessions.push(sessionData)
              } catch (e) {
                console.error('解析头脑风暴会话失败:', e)
              }
            }

            if (allSessions.length > 0) {
              // 最新的讨论作为当前会话（如果它已完成）
              const latestSession = allSessions[0]
              if (latestSession.isComplete) {
                brainstormSession.value = latestSession
              }

              // 所有记录作为历史记录
              brainstormHistory.value = allSessions
            }
          } catch (e) {
            console.error('恢复头脑风暴会话失败:', e)
          }
        }
      } else {
        // 如果不是头脑风暴Agent，清除头脑风暴状态
        brainstormSession.value = null
        brainstormHistory.value = []
        currentRound.value = 0
        currentSpeaker.value = null
      }
    } catch (error) {
      console.error('获取对话历史失败:', error)
    }
  }

  // 建立WebSocket连接
  const connectWebSocket = async (sessionId: number) => {
    const authStore = useAuthStore()
    if (!authStore.token) {
      throw new Error('用户未登录，请重新登录')
    }

    try {
      await websocketService.connect(sessionId.toString(), authStore.token)
      wsConnected.value = true

      // 设置消息处理器
      websocketService.onMessage('agent_response', (data) => {
        // 收到第一个响应时，清除等待状态
        if (isWaitingForResponse.value) {
          isWaitingForResponse.value = false
        }

        // 检查是否是头脑风暴Agent
        if (currentAgent.value?.type === 'brainstorm_agent') {
          handleBrainstormResponse(data)
        } else {
          // 普通Agent的处理逻辑
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
            streamingMetadata.value = data.metadata
            isStreaming.value = true
          }
        }
      })

      websocketService.onMessage('error', (data) => {
        console.error('WebSocket错误:', data)
        isStreaming.value = false
        isWaitingForResponse.value = false
        streamingMessage.value = ''
        streamingMetadata.value = null
      })

      // 处理会话标题自动更新
      websocketService.onMessage('session_title_updated', (data) => {
        const { session_id, new_title } = data
        console.log(`会话 ${session_id} 标题已更新: ${new_title}`)

        // 更新会话列表中的标题
        const sessionIndex = sessions.value.findIndex(s => s.id === session_id)
        if (sessionIndex !== -1) {
          sessions.value[sessionIndex].name = new_title
        }

        // 如果是当前会话，也更新当前会话的标题
        if (currentSession.value?.id === session_id) {
          currentSession.value.name = new_title
        }
      })

    } catch (error) {
      console.error('WebSocket连接失败:', error)
      wsConnected.value = false

      // 提供更友好的错误信息
      if (error instanceof Error) {
        if (error.message.includes('401') || error.message.includes('Unauthorized')) {
          throw new Error('身份验证失败，请重新登录')
        } else if (error.message.includes('404')) {
          throw new Error('会话不存在，请刷新页面重试')
        } else if (error.message.includes('timeout')) {
          throw new Error('连接超时，请检查网络状态')
        }
      }

      throw new Error('连接服务器失败，请检查网络状态后重试')
    }
  }

  // 处理头脑风暴响应
  const handleBrainstormResponse = (data: any) => {
    const metadata = data.metadata
    const phase = metadata?.discussion_phase

    if (phase === 'start') {
      // 提取主题内容
      let topic = data.content
      if (topic.includes('🎯 **讨论主题**: ')) {
        topic = topic.replace('🎯 **讨论主题**: ', '').replace(/\n+/g, '').trim()
      }

      // 如果没有从响应中获取到主题，尝试从最近的用户消息中获取
      if (!topic || topic === '') {
        const lastUserMessage = conversations.value
          .filter(conv => conv.message_type === 'user')
          .pop()
        topic = lastUserMessage?.content || '未知主题'
      }

      // 初始化头脑风暴会话
      brainstormSession.value = {
        topic: topic,
        config: {
          model_a: metadata.model_a,
          model_b: metadata.model_b,
          style: metadata.style,
          max_rounds: metadata.max_rounds
        },
        rounds: [],
        isComplete: false
      }
      currentRound.value = 0
      currentSpeaker.value = null
    } else if (phase === 'model_a_start' || phase === 'model_b_start') {
      // 模型开始发言
      const roundNum = metadata.round
      const isModelA = phase === 'model_a_start'

      // 确保轮次存在
      if (!brainstormSession.value?.rounds.find(r => r.round === roundNum)) {
        brainstormSession.value?.rounds.push({
          round: roundNum,
          modelA: { content: '', isStreaming: false, isComplete: false },
          modelB: { content: '', isStreaming: false, isComplete: false }
        })
      }

      currentRound.value = roundNum
      currentSpeaker.value = isModelA ? 'model_a' : 'model_b'

      // 设置当前发言者为流式状态
      const round = brainstormSession.value?.rounds.find(r => r.round === roundNum)
      if (round) {
        if (isModelA) {
          round.modelA.isStreaming = true
          round.modelA.content = ''
        } else {
          round.modelB.isStreaming = true
          round.modelB.content = ''
        }
      }
    } else if (phase === 'model_a_speaking' || phase === 'model_b_speaking') {
      // 模型正在发言
      const roundNum = metadata.round
      const isModelA = phase === 'model_a_speaking'

      const round = brainstormSession.value?.rounds.find(r => r.round === roundNum)
      if (round) {
        if (isModelA) {
          round.modelA.content += data.content
        } else {
          round.modelB.content += data.content
        }
      }
    } else if (data.content === '\n\n' || data.content === '\n\n---\n\n') {
      // 模型发言结束标记
      if (currentSpeaker.value && currentRound.value > 0) {
        const round = brainstormSession.value?.rounds.find(r => r.round === currentRound.value)
        if (round) {
          if (currentSpeaker.value === 'model_a') {
            round.modelA.isStreaming = false
            round.modelA.isComplete = true
          } else {
            round.modelB.isStreaming = false
            round.modelB.isComplete = true
          }
        }
        currentSpeaker.value = null
      }
    } else if (phase === 'summary_start') {
      // 开始总结
      brainstormSession.value!.summary = ''
    } else if (phase === 'summary') {
      // 总结内容
      brainstormSession.value!.summary += data.content
    } else if (phase === 'complete') {
      // 讨论完成
      brainstormSession.value!.isComplete = true

      // 标记所有轮次为完成状态
      brainstormSession.value?.rounds.forEach(round => {
        round.modelA.isStreaming = false
        round.modelA.isComplete = true
        round.modelB.isStreaming = false
        round.modelB.isComplete = true
      })

      currentSpeaker.value = null
      isStreaming.value = false

      // 将完整的头脑风暴会话添加到对话历史
      if (brainstormSession.value) {
        const sessionRecord = {
          id: Date.now(),
          session_id: currentSession.value!.id,
          message_type: 'assistant' as const,
          content: JSON.stringify(brainstormSession.value), // 序列化整个会话
          extra_data: { type: 'brainstorm_session' },
          created_at: new Date().toISOString(),
        }

        // 总是添加新记录，支持多轮讨论
        conversations.value.push(sessionRecord)

        // 更新历史记录
        brainstormHistory.value.unshift(brainstormSession.value)
      }
    }

    // 如果不是最终响应，设置流式状态
    if (!data.is_final) {
      isStreaming.value = true
    }
  }

  // 确保WebSocket连接已建立
  const ensureWebSocketConnection = async (sessionId: number): Promise<void> => {
    if (wsConnected.value) {
      return // 已连接，无需重复建立
    }

    try {
      await connectWebSocket(sessionId)
      if (!wsConnected.value) {
        throw new Error('WebSocket连接建立失败')
      }
    } catch (error) {
      console.error('建立WebSocket连接失败:', error)
      throw new Error('无法建立连接，请检查网络状态后重试')
    }
  }

  // 发送消息
  const sendMessage = async (content: string) => {
    if (!currentSession.value) {
      throw new Error('没有活动会话')
    }

    let targetSessionId: number

    // 如果是临时会话，先转换为正式会话
    if (currentSession.value.isTemporary) {
      try {
        const realSession = await convertTemporaryToRealSession(currentSession.value as TemporarySession)
        targetSessionId = realSession.id
      } catch (error) {
        console.error('转换临时会话失败:', error)
        throw new Error('无法创建会话，请重试')
      }
    } else {
      targetSessionId = currentSession.value.id
    }

    // 确保WebSocket连接已建立
    try {
      await ensureWebSocketConnection(targetSessionId)
    } catch (error) {
      // 连接失败，但仍然允许用户重试
      throw error
    }

    // 添加用户消息到对话历史
    const userMessage: Conversation = {
      id: Date.now(), // 临时ID
      session_id: targetSessionId,
      message_type: 'user',
      content,
      created_at: new Date().toISOString(),
    }
    conversations.value.push(userMessage)

    // 如果是头脑风暴Agent，重置相关状态（但保留历史记录）
    if (currentAgent.value?.type === 'brainstorm_agent') {
      brainstormSession.value = null
      currentRound.value = 0
      currentSpeaker.value = null
      // 注意：不清除brainstormHistory，保留历史讨论记录
    }

    // 设置等待响应状态
    isWaitingForResponse.value = true
    streamingMessage.value = ''
    streamingMetadata.value = null
    isStreaming.value = false

    // 发送WebSocket消息
    try {
      websocketService.sendUserMessage(content)
    } catch (error) {
      // 发送失败，重置状态
      isWaitingForResponse.value = false
      console.error('发送WebSocket消息失败:', error)
      throw new Error('消息发送失败，请重试')
    }
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

      // 清空头脑风暴相关状态
      brainstormSession.value = null
      brainstormHistory.value = []
      currentRound.value = 0
      currentSpeaker.value = null

      // 清空流式消息状态
      streamingMessage.value = ''
      streamingMetadata.value = null
      isStreaming.value = false
      isWaitingForResponse.value = false
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
    streamingMetadata,
    isStreaming,
    isWaitingForResponse,

    // 双模型头脑风暴状态
    brainstormSession,
    brainstormHistory,
    currentRound,
    currentSpeaker,

    // 计算属性
    currentAgent,
    filteredSessions,
    sortedSessions,
    hasActiveChat,

    // 方法
    fetchAgents,
    fetchSessions,
    setCurrentAgent,
    createSession,
    setCurrentSession,
    fetchConversations,
    connectWebSocket,
    ensureWebSocketConnection,
    sendMessage,
    updateSessionName,
    deleteSession,
    clearConversations,
    disconnectWebSocket,
    handleBrainstormResponse,

    // 新增：临时会话管理方法
    createTemporarySession,
    clearTemporarySession,
    convertTemporaryToRealSession,
  }
})

// 导入useAuthStore（避免循环依赖）
import { useAuthStore } from './auth'
