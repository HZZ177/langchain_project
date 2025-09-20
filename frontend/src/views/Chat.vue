<template>
  <div class="flex h-screen bg-gray-50">
    <!-- 侧边栏 -->
    <div class="w-80 bg-white border-r border-gray-200 flex flex-col">
      <!-- 头部 -->
      <div class="p-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h1 class="text-xl font-semibold text-gray-900">AI Agent平台</h1>
          <div class="flex items-center space-x-2">
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
        <div v-if="showUserMenu" class="absolute right-4 top-16 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
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

      <!-- 新建对话按钮 -->
      <div class="p-4">
        <button
          @click="showNewChatModal = true"
          class="w-full btn-primary flex items-center justify-center space-x-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>新建对话</span>
        </button>
      </div>

      <!-- 会话列表 -->
      <div class="flex-1 overflow-y-auto">
        <div class="p-2 space-y-1">
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
                  {{ getAgentName(session.agent_id) }}
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
    </div>

    <!-- 主聊天区域 -->
    <div class="flex-1 flex flex-col">
      <div v-if="!chatStore.currentSession" class="flex-1 flex items-center justify-center">
        <div class="text-center">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a8.959 8.959 0 01-4.906-1.681L3 21l2.681-5.094A8.959 8.959 0 013 12c0-4.418 3.582-8 8-8s8 3.582 8 8z" />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">选择一个对话开始聊天</h3>
          <p class="mt-1 text-sm text-gray-500">或者创建一个新的对话</p>
        </div>
      </div>

      <div v-else class="flex-1 flex flex-col">
        <!-- 聊天头部 -->
        <div class="bg-white border-b border-gray-200 p-4">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-lg font-semibold text-gray-900">{{ chatStore.currentSession.name }}</h2>
              <p class="text-sm text-gray-500">{{ chatStore.currentAgent?.name }}</p>
            </div>
            <div class="flex items-center space-x-2">
              <div class="flex items-center space-x-1">
                <div
                  class="w-2 h-2 rounded-full"
                  :class="chatStore.wsConnected ? 'bg-green-500' : 'bg-red-500'"
                ></div>
                <span class="text-xs text-gray-500">
                  {{ chatStore.wsConnected ? '已连接' : '未连接' }}
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
        <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-4">
          <div
            v-for="conversation in chatStore.conversations"
            :key="conversation.id"
            class="flex"
            :class="{
              'justify-end': conversation.message_type === 'user',
              'justify-start': conversation.message_type === 'assistant'
            }"
          >
            <div
              class="max-w-xs lg:max-w-md px-4 py-2 rounded-lg"
              :class="{
                'bg-primary-600 text-white': conversation.message_type === 'user',
                'bg-white border border-gray-200 text-gray-900': conversation.message_type === 'assistant'
              }"
            >
              <div class="whitespace-pre-wrap">{{ conversation.content }}</div>
              <div class="text-xs mt-1 opacity-70">
                {{ formatTime(conversation.created_at) }}
              </div>
            </div>
          </div>

          <!-- Loading气泡 -->
          <LoadingBubble v-if="chatStore.isWaitingForResponse" />

          <!-- 流式消息 -->
          <div v-if="chatStore.isStreaming && chatStore.streamingMessage" class="flex justify-start">
            <div class="max-w-xs lg:max-w-md px-4 py-2 rounded-lg bg-white border border-gray-200 text-gray-900">
              <div class="whitespace-pre-wrap">{{ chatStore.streamingMessage }}</div>
              <div class="flex items-center mt-1">
                <div class="flex space-x-1">
                  <div class="w-1 h-1 bg-gray-400 rounded-full animate-bounce"></div>
                  <div class="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                  <div class="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="bg-white border-t border-gray-200 p-4">
          <form @submit.prevent="sendMessage" class="flex space-x-4">
            <div class="flex-1">
              <textarea
                v-model="messageInput"
                @keydown.enter.exact.prevent="sendMessage"
                @keydown.enter.shift.exact="addNewLine"
                placeholder="输入消息... (Enter发送，Shift+Enter换行)"
                rows="1"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                :disabled="!chatStore.wsConnected || chatStore.isStreaming || chatStore.isWaitingForResponse"
              ></textarea>
            </div>
            <button
              type="submit"
              :disabled="!messageInput.trim() || !chatStore.wsConnected || chatStore.isStreaming || chatStore.isWaitingForResponse"
              class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- 新建对话模态框 -->
    <div v-if="showNewChatModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-96 max-w-md mx-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">新建对话</h3>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">选择Agent</label>
            <select
              v-model="newChatForm.agentId"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">请选择Agent</option>
              <option
                v-for="agent in chatStore.agents"
                :key="agent.id"
                :value="agent.id"
              >
                {{ agent.name }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">对话名称</label>
            <input
              v-model="newChatForm.name"
              type="text"
              placeholder="新对话"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>

        <div class="flex justify-end space-x-3 mt-6">
          <button
            @click="showNewChatModal = false"
            class="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300"
          >
            取消
          </button>
          <button
            @click="createNewChat"
            :disabled="!newChatForm.agentId"
            class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            创建
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import LoadingBubble from '@/components/LoadingBubble.vue'
import type { Session } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()

// 响应式数据
const showUserMenu = ref(false)
const showNewChatModal = ref(false)
const messageInput = ref('')
const messagesContainer = ref<HTMLElement>()

const newChatForm = ref({
  agentId: '',
  name: '新对话'
})

// 生命周期
onMounted(async () => {
  // 获取Agent列表和会话列表
  await Promise.all([
    chatStore.fetchAgents(),
    chatStore.fetchSessions()
  ])

  // 如果有会话但没有当前会话，选择第一个
  if (chatStore.sessions.length > 0 && !chatStore.currentSession) {
    await selectSession(chatStore.sessions[0])
  }
})

onUnmounted(() => {
  // 断开WebSocket连接
  chatStore.disconnectWebSocket()
})

// 监听对话变化，自动滚动到底部
watch(
  () => [chatStore.conversations, chatStore.streamingMessage, chatStore.isWaitingForResponse],
  () => {
    nextTick(() => {
      scrollToBottom()
    })
  },
  { deep: true }
)

// 方法
const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

const selectSession = async (session: Session) => {
  try {
    await chatStore.setCurrentSession(session)
  } catch (error) {
    console.error('选择会话失败:', error)
  }
}

const createNewChat = async () => {
  try {
    const session = await chatStore.createSession(
      parseInt(newChatForm.value.agentId),
      newChatForm.value.name || '新对话'
    )

    showNewChatModal.value = false
    newChatForm.value = { agentId: '', name: '新对话' }

    await selectSession(session)
  } catch (error) {
    console.error('创建对话失败:', error)
  }
}

const sendMessage = async () => {
  const content = messageInput.value.trim()
  if (!content || !chatStore.wsConnected || chatStore.isStreaming || chatStore.isWaitingForResponse) return

  try {
    await chatStore.sendMessage(content)
    messageInput.value = ''
  } catch (error) {
    console.error('发送消息失败:', error)
  }
}

const addNewLine = () => {
  messageInput.value += '\n'
}

const deleteSession = async (sessionId: number) => {
  if (confirm('确定要删除这个对话吗？')) {
    try {
      await chatStore.deleteSession(sessionId)
    } catch (error) {
      console.error('删除会话失败:', error)
    }
  }
}

const clearConversations = async () => {
  if (confirm('确定要清空当前对话历史吗？')) {
    try {
      await chatStore.clearConversations()
    } catch (error) {
      console.error('清空对话失败:', error)
    }
  }
}

const getAgentName = (agentId: number) => {
  const agent = chatStore.agents.find(a => a.id === agentId)
  return agent?.name || 'Unknown Agent'
}

const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 点击外部关闭用户菜单
const handleClickOutside = (event: Event) => {
  const target = event.target as HTMLElement
  if (!target.closest('.user-menu')) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
