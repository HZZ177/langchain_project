<template>
  <div class="flex h-screen bg-gray-50">
    <!-- 侧边栏 -->
    <div class="w-80 bg-white border-r border-gray-200 flex flex-col">
      <!-- 头部 -->
      <div class="p-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h1 class="text-xl font-semibold text-gray-900">AI Agent平台</h1>
          <div class="flex items-center space-x-2">
            <!-- 配置按钮 -->
            <button
              @click="showConfigModal = true"
              class="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
              title="Agent配置"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>
            <!-- 用户头像按钮 -->
            <button
              @click="showUserMenu = !showUserMenu"
              class="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>

        <!-- 用户菜单 -->
        <div v-if="showUserMenu" class="absolute right-4 top-16 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-10 user-menu">
          <div class="p-3 border-b border-gray-200">
            <p class="text-sm font-medium text-gray-900">{{ authStore.user?.username }}</p>
            <p class="text-xs text-gray-500">{{ authStore.user?.email }}</p>
          </div>
          <div class="p-1">
            <button
              @click="handleLogout"
              class="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
            >
              退出登录
            </button>
          </div>
        </div>
      </div>

      <!-- Agent选择器 -->
      <div class="p-4 border-b border-gray-200">
        <div class="relative agent-dropdown">
          <button
            @click="showAgentDropdown = !showAgentDropdown"
            class="w-full flex items-center justify-between px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <div class="flex items-center space-x-2">
              <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <span class="text-sm font-medium text-gray-900">
                {{ chatStore.currentAgent?.name || '选择Agent' }}
              </span>
            </div>
            <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          <!-- Agent下拉菜单 -->
          <div v-if="showAgentDropdown" class="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-20">
            <div class="py-1">
              <button
                v-for="agent in chatStore.agents"
                :key="agent.id"
                @click="selectAgent(agent.id)"
                class="w-full text-left px-3 py-2 text-sm hover:bg-gray-100 flex items-center space-x-2"
                :class="{
                  'bg-primary-50 text-primary-700': chatStore.currentAgentId === agent.id,
                  'text-gray-900': chatStore.currentAgentId !== agent.id
                }"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <span>{{ agent.name }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 会话列表 -->
      <div class="flex-1 overflow-y-auto">
        <div v-if="!chatStore.currentAgentId" class="p-4 text-center text-gray-500">
          <p class="text-sm">请先选择一个Agent</p>
        </div>
        <div v-else-if="chatStore.sortedSessions.length === 0" class="p-4 text-center text-gray-500">
          <p class="text-sm">暂无对话</p>
          <p class="text-xs mt-1">点击下方按钮创建新对话</p>
        </div>
        <div v-else class="p-2 space-y-1">
          <div
            v-for="session in chatStore.sortedSessions"
            :key="session.id"
            @click="selectSession(session)"
            class="p-3 rounded-lg cursor-pointer transition-colors"
            :class="{
              'bg-primary-50 border border-primary-200': chatStore.currentSession?.id === session.id,
              'hover:bg-gray-50': chatStore.currentSession?.id !== session.id
            }"
          >
            <div class="flex items-center justify-between">
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">
                  {{ session.name }}
                </p>
                <p class="text-xs text-gray-500 mt-1">
                  {{ formatTime(session.updated_at) }}
                </p>
              </div>
              <button
                @click.stop="deleteSession(session.id)"
                class="p-1 text-gray-400 hover:text-red-500 rounded"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 新建对话按钮 - 选中Agent时显示 -->
      <div v-if="chatStore.currentAgentId" class="border-t border-gray-200 p-4">
        <button
          @click="createNewChat"
          :disabled="!chatStore.currentAgentId"
          class="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>新建对话</span>
        </button>
      </div>
    </div>

    <!-- Agent配置弹窗 -->
    <AgentConfigModal
      v-if="showConfigModal"
      :agents="chatStore.agents"
      @close="showConfigModal = false"
      @config-saved="handleConfigSaved"
    />

    <!-- 主聊天区域 -->
    <div class="flex-1 flex flex-col">
      <div v-if="!chatStore.hasActiveChat" class="flex-1 flex items-center justify-center">
        <div class="text-center">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a8.959 8.959 0 01-4.906-1.681L3 21l2.681-5.094A8.959 8.959 0 013 12c0-4.418 3.582-8 8-8s8 3.582 8 8z" />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">选择一个Agent开始聊天</h3>
          <p class="mt-1 text-sm text-gray-500">选择上方的Agent即可开始对话</p>
        </div>
      </div>

      <div v-else class="flex-1 flex flex-col min-h-0">
        <!-- 聊天头部 -->
        <div class="bg-white border-b border-gray-200 p-4 flex-shrink-0">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-lg font-semibold text-gray-900 flex items-center space-x-2">
                <span>{{ chatStore.currentSession.name }}</span>
                <span v-if="chatStore.currentSession.isTemporary" class="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded-full">
                  临时会话
                </span>
              </h2>
              <p class="text-sm text-gray-500">{{ chatStore.currentAgent?.name }}</p>
            </div>
            <div class="flex items-center space-x-2">
              <div class="flex items-center space-x-1">
                <div
                  class="w-2 h-2 rounded-full"
                  :class="chatStore.wsConnected ? 'bg-green-500' : 'bg-yellow-500'"
                ></div>
                <span class="text-xs text-gray-500">
                  {{ chatStore.wsConnected ? '已连接' : '待连接' }}
                </span>
              </div>
              <button
                @click="clearConversations"
                class="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
                title="清空对话"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- 消息列表 -->
        <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
          <!-- 头脑风暴Agent的特殊显示 -->
          <div v-if="isBrainstormAgent">
            <!-- 显示历史讨论（除了当前正在进行的讨论） -->
            <div v-for="(historySession, index) in chatStore.brainstormHistory" :key="`history-${index}`">
              <!-- 只显示已完成的历史讨论，且不是当前正在进行的讨论 -->
              <div v-if="historySession.isComplete && historySession !== chatStore.brainstormSession" class="mb-6">
                <div class="text-xs text-gray-400 mb-2 flex items-center">
                  <span class="mr-2">📝</span>
                  <span>历史讨论 {{ chatStore.brainstormHistory.length - index }}</span>
                  <div class="flex-1 border-t border-gray-200 ml-3"></div>
                </div>
                <BrainstormDiscussion :discussion-data="historySession" />
              </div>
            </div>

            <!-- 显示当前的头脑风暴会话 -->
            <BrainstormDiscussion
              v-if="chatStore.brainstormSession || enhancedBrainstormData"
              :discussion-data="enhancedBrainstormData || chatStore.brainstormSession"
            />

            <!-- Loading状态 -->
            <div v-if="chatStore.isWaitingForResponse && !chatStore.brainstormSession" class="text-center py-8">
              <LoadingBubble />
              <p class="text-sm text-gray-500 mt-2">正在初始化双模型讨论...</p>
            </div>
          </div>

          <!-- 普通Agent的消息显示 -->
          <div v-else>
            <!-- 历史消息 -->
            <ChatMessage
              v-for="conversation in chatStore.conversations"
              :key="conversation.id"
              :message="{
                message_type: conversation.message_type,
                content: conversation.content,
                timestamp: conversation.created_at
              }"
            />

            <!-- Loading状态 -->
            <div v-if="chatStore.isWaitingForResponse && !chatStore.isStreaming" class="flex justify-start">
              <div class="flex items-center gap-3">
                <div class="avatar">
                  <div class="w-9 h-9 bg-gray-500 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                    AI
                  </div>
                </div>
                <div class="bg-white border border-gray-200 rounded-2xl px-4 py-3">
                  <div class="flex items-center space-x-2">
                    <div class="flex space-x-1">
                      <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                      <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                    </div>
                    <span class="text-sm text-gray-500">AI正在思考...</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 流式消息 -->
            <ChatMessage
              v-if="chatStore.isStreaming && chatStore.streamingMessage"
              :message="{
                message_type: 'assistant',
                content: chatStore.streamingMessage,
                timestamp: new Date().toISOString()
              }"
              :is-streaming="true"
              :show-header="false"
            />
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="bg-white border-t border-gray-200 p-4 flex-shrink-0">
          <form @submit.prevent="sendMessage">
            <!-- 输入容器 -->
            <div class="border border-gray-300 rounded-2xl bg-white hover:border-gray-400 focus-within:border-gray-400 transition-colors duration-150">
              <!-- 文本输入区域 -->
              <div class="px-4 py-1.5 flex items-center">
                <textarea
                  ref="messageTextarea"
                  v-model="messageInput"
                  @input="autoResize"
                  @keydown.enter.exact.prevent="sendMessage"
                  @keydown.enter.shift.exact.prevent="addNewLine"
                  :placeholder="chatStore.isStreaming || chatStore.isWaitingForResponse ? '可以继续输入，AI回复完成后即可发送...' : '你想知道什么？'"
                  class="w-full min-h-[40px] max-h-[200px] bg-transparent border-0 resize-none focus:outline-none placeholder-gray-500 leading-6 py-2"
                  :class="{ 'bg-gray-50': chatStore.isStreaming || chatStore.isWaitingForResponse }"
                  style="field-sizing: content;"
                ></textarea>
              </div>

              <!-- 功能区域 -->
              <div class="flex items-center justify-between px-4 py-1.5">
                <!-- 左侧功能按钮区域 -->
                <div class="flex items-center space-x-2">
                  <!-- 上传文件按钮 -->
                  <button
                    type="button"
                    @click="handleUploadClick"
                    class="w-10 h-10 rounded-full flex items-center justify-center text-gray-500 hover:text-gray-700 hover:bg-gray-100 border border-gray-300 hover:border-gray-400 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-gray-400"
                    title="上传文件"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                    </svg>
                  </button>
                </div>

                <!-- 右侧发送按钮 -->
                <button
                  type="submit"
                  :disabled="!messageInput.trim() || chatStore.isStreaming || chatStore.isWaitingForResponse"
                  class="w-10 h-10 rounded-full flex items-center justify-center transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-gray-400"
                  :class="[
                    messageInput.trim() && !chatStore.isStreaming && !chatStore.isWaitingForResponse
                      ? 'bg-gray-900 text-white hover:bg-gray-800'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  ]"
                  :title="chatStore.isStreaming || chatStore.isWaitingForResponse ? 'AI正在回复中，请稍候...' : '发送消息'"
                >
                  <!-- 加载状态 -->
                  <svg v-if="chatStore.isStreaming || chatStore.isWaitingForResponse" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <!-- 发送图标 -->
                  <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>


  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import { useNotification } from '@/composables/useNotification'
import LoadingBubble from '@/components/LoadingBubble.vue'
import AgentConfigModal from '@/components/AgentConfigModal.vue'
import BrainstormDiscussion from '@/components/BrainstormDiscussion.vue'
import ChatMessage from '@/components/ChatMessage.vue'
import type { Session } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()
const notification = useNotification()

// 响应式数据
const showUserMenu = ref(false)
const showAgentDropdown = ref(false)
const showConfigModal = ref(false)
const messageInput = ref('')
const messagesContainer = ref<HTMLElement>()
const messageTextarea = ref<HTMLTextAreaElement>()

// 滚动状态管理
const isUserScrolling = ref(false) // 用户是否主动滚动
const isNearBottom = ref(true) // 是否在底部附近
const scrollThreshold = 100 // 距离底部多少像素认为是"接近底部"

// 计算属性
const isBrainstormAgent = computed(() => {
  return chatStore.currentAgent?.type === 'brainstorm_agent'
})

const userMessages = computed(() => {
  return chatStore.conversations.filter(conv => conv.message_type === 'user')
})

// 增强的头脑风暴数据，确保即使后端没有正确初始化也能显示用户主题
const enhancedBrainstormData = computed(() => {
  // 优先使用store中的头脑风暴会话数据
  if (chatStore.brainstormSession) {
    return chatStore.brainstormSession
  }

  // 如果没有头脑风暴会话但有用户消息，且没有任何助手消息，创建一个基础的会话数据
  // 这种情况通常发生在刚发送消息但还没收到响应时
  if (isBrainstormAgent.value && userMessages.value.length > 0) {
    const hasAssistantMessages = chatStore.conversations.some(conv => conv.message_type === 'assistant')

    if (!hasAssistantMessages) {
      const lastUserMessage = userMessages.value[userMessages.value.length - 1]
      return {
        topic: lastUserMessage.content,
        config: {
          model_a: "GPT-4",
          model_b: "Claude-3",
          style: "collaborative" as const,
          max_rounds: 3
        },
        rounds: [],
        isComplete: false
      }
    }
  }

  return null
})
// 生命周期
onMounted(async () => {
  // 获取Agent列表和会话列表
  await Promise.all([
    chatStore.fetchAgents(),
    chatStore.fetchSessions()
  ])

  // 添加滚动事件监听器
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.addEventListener('scroll', handleScroll, { passive: true })
    }
  })
})

onUnmounted(() => {
  // 清理临时会话
  chatStore.clearTemporarySession()

  // 断开WebSocket连接
  chatStore.disconnectWebSocket()

  // 清理资源

  // 移除滚动事件监听器
  if (messagesContainer.value) {
    messagesContainer.value.removeEventListener('scroll', handleScroll)
  }
})

// 监听对话变化，智能滚动到底部
watch(
  () => [chatStore.conversations, chatStore.streamingMessage, chatStore.isWaitingForResponse, chatStore.brainstormSession],
  () => {
    nextTick(() => {
      // 只有在用户位于底部附近时才自动滚动
      if (isNearBottom.value && !isUserScrolling.value) {
        scrollToBottom(false) // false表示这是自动滚动
      }
    })
  },
  { deep: true }
)

// 方法
const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

const selectAgent = async (agentId: number) => {
  try {
    await chatStore.setCurrentAgent(agentId)
    showAgentDropdown.value = false
  } catch (error) {
    notification.handleError(error, '选择Agent失败')
  }
}

const selectSession = async (session: Session) => {
  try {
    await chatStore.setCurrentSession(session)
  } catch (error) {
    notification.handleError(error, '选择会话失败')
  }
}

const createNewChat = async () => {
  try {
    const session = await chatStore.createSession()
    await selectSession(session)
    notification.success('新对话创建成功')
  } catch (error) {
    notification.handleError(error, '创建对话失败')
  }
}

const sendMessage = async () => {
  const content = messageInput.value.trim()
  if (!content || chatStore.isStreaming || chatStore.isWaitingForResponse) return

  try {
    await chatStore.sendMessage(content)
    messageInput.value = ''
  } catch (error) {
    notification.handleError(error, '发送消息失败')
  }
}

// 简单的自动调整高度函数
const autoResize = () => {
  // 新的CSS方案使用field-sizing: content，浏览器自动处理高度
  // 这里可以添加任何需要的额外逻辑
}

const addNewLine = () => {
  messageInput.value += '\n'
}

const handleUploadClick = () => {
  notification.info('文件上传功能开发中，敬请期待！')
}



const deleteSession = async (sessionId: number) => {
  const confirmed = await notification.confirm({
    title: '删除对话',
    message: '确定要删除这个对话吗？此操作无法撤销。',
    confirmText: '删除',
    cancelText: '取消'
  })

  if (confirmed) {
    try {
      await chatStore.deleteSession(sessionId)
      notification.success('对话删除成功')
    } catch (error) {
      notification.handleError(error, '删除会话失败')
    }
  }
}

const clearConversations = async () => {
  const confirmed = await notification.confirm({
    title: '清空对话历史',
    message: '确定要清空当前对话历史吗？此操作无法撤销。',
    confirmText: '清空',
    cancelText: '取消'
  })

  if (confirmed) {
    try {
      await chatStore.clearConversations()
      notification.success('对话历史清空成功')
    } catch (error) {
      notification.handleError(error, '清空对话失败')
    }
  }
}



const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleConfigSaved = () => {
  notification.success('配置保存成功')
  showConfigModal.value = false
}

const scrollToBottom = (isUserAction = true) => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight

    // 如果是用户主动操作，更新状态
    if (isUserAction) {
      isNearBottom.value = true
      isUserScrolling.value = false
    }
  }
}

// 检查是否接近底部
const checkIfNearBottom = () => {
  if (!messagesContainer.value) return

  const { scrollTop, scrollHeight, clientHeight } = messagesContainer.value
  const distanceFromBottom = scrollHeight - scrollTop - clientHeight

  isNearBottom.value = distanceFromBottom <= scrollThreshold
}

// 处理用户滚动事件
const handleScroll = () => {
  isUserScrolling.value = true
  checkIfNearBottom()

  // 500ms后重置用户滚动状态，允许自动滚动
  setTimeout(() => {
    isUserScrolling.value = false
  }, 500)
}

// 点击外部关闭菜单
const handleClickOutside = (event: Event) => {
  const target = event.target as HTMLElement
  if (!target.closest('.user-menu')) {
    showUserMenu.value = false
  }
  if (!target.closest('.agent-dropdown')) {
    showAgentDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)

  // 确保滚动事件监听器被正确添加
  nextTick(() => {
    if (messagesContainer.value && !messagesContainer.value.onscroll) {
      messagesContainer.value.addEventListener('scroll', handleScroll, { passive: true })
    }
  })
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* 自定义消息容器滚动条样式 */
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e0 #f7fafc;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f7fafc;
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

/* 确保flex容器正确处理高度 */
.min-h-0 {
  min-height: 0;
}
</style>
