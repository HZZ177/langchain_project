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

      <!-- 新建对话按钮 -->
      <div class="border-t border-gray-200 p-4">
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
          >
            <!-- 头脑风暴Agent的消息显示 -->
            <BrainstormChatMessage
              v-if="isBrainstormAgent && conversation.message_type === 'assistant'"
              :message="conversation"
            />

            <!-- 普通消息显示 -->
            <div
              v-else
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
          </div>

          <!-- Loading气泡 -->
          <LoadingBubble v-if="chatStore.isWaitingForResponse" />

          <!-- 流式消息 -->
          <div v-if="chatStore.isStreaming && chatStore.streamingMessage">
            <!-- 头脑风暴Agent的流式消息 -->
            <BrainstormChatMessage
              v-if="isBrainstormAgent"
              :message="{ content: chatStore.streamingMessage, metadata: chatStore.streamingMetadata }"
            />

            <!-- 普通Agent的流式消息 -->
            <div v-else class="flex justify-start">
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
        </div>

        <!-- 输入区域 -->
        <div class="bg-white border-t border-gray-200 p-4">
          <form @submit.prevent="sendMessage" class="flex space-x-4">
            <div class="flex-1">
              <div class="relative">
                <!-- 拖拽手柄 -->
                <div
                  class="absolute top-0 left-0 right-0 h-4 cursor-ns-resize flex items-center justify-center group hover:bg-gray-50 transition-colors duration-200 z-10"
                  @mousedown="startDragging"
                  title="向上拖拽增加输入框高度"
                >
                  <div class="w-12 h-1 bg-gray-300 rounded-full group-hover:bg-gray-500 transition-colors duration-200"></div>
                </div>

                <textarea
                  ref="messageTextarea"
                  v-model="messageInput"
                  @input="adjustTextareaHeight"
                  @keydown.enter.exact.prevent="sendMessage"
                  @keydown.enter.shift.exact="addNewLine"
                  placeholder="输入消息... (Enter发送，Shift+Enter换行)"
                  rows="1"
                  :style="{ height: textareaHeight + 'px', paddingTop: '20px' }"
                  :class="[
                    'w-full px-3 pb-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none',
                    { 'transition-all duration-200 ease-in-out': !isDragging }
                  ]"
                  :disabled="!chatStore.wsConnected || chatStore.isStreaming || chatStore.isWaitingForResponse"
                ></textarea>
              </div>
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
import BrainstormChatMessage from '@/components/BrainstormChatMessage.vue'
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

// 输入框高度相关
const textareaHeight = ref(56) // 默认高度（包含上方拖拽区域）
const minHeight = 56 // 最小高度（包含上方拖拽区域）

// 计算属性
const isBrainstormAgent = computed(() => {
  return chatStore.selectedAgent?.type === 'brainstorm_agent'
})
const maxHeight = 220 // 最大高度（包含上方拖拽区域）
const isDragging = ref(false)
const dragStartY = ref(0)
const dragStartHeight = ref(0)
const animationFrameId = ref<number | null>(null)

// 生命周期
onMounted(async () => {
  // 获取Agent列表和会话列表
  await Promise.all([
    chatStore.fetchAgents(),
    chatStore.fetchSessions()
  ])

  // 如果当前Agent下有会话但没有当前会话，选择第一个
  if (chatStore.sortedSessions.length > 0 && !chatStore.currentSession) {
    await selectSession(chatStore.sortedSessions[0])
  }

  // 初始化输入框高度
  nextTick(() => {
    if (messageTextarea.value) {
      messageTextarea.value.style.height = minHeight + 'px'
    }
  })
})

onUnmounted(() => {
  // 断开WebSocket连接
  chatStore.disconnectWebSocket()

  // 清理拖拽相关资源
  if (animationFrameId.value) {
    cancelAnimationFrame(animationFrameId.value)
  }
  document.removeEventListener('mousemove', handleDragging)
  document.removeEventListener('mouseup', stopDragging)
  document.body.style.userSelect = ''
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

const selectAgent = (agentId: number) => {
  chatStore.setCurrentAgent(agentId)
  showAgentDropdown.value = false
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
  if (!content || !chatStore.wsConnected || chatStore.isStreaming || chatStore.isWaitingForResponse) return

  try {
    await chatStore.sendMessage(content)
    messageInput.value = ''
    // 重置输入框高度
    textareaHeight.value = minHeight
    if (messageTextarea.value) {
      messageTextarea.value.style.height = minHeight + 'px'
    }
  } catch (error) {
    notification.handleError(error, '发送消息失败')
  }
}

const addNewLine = () => {
  messageInput.value += '\n'
  // 添加换行后调整高度
  nextTick(() => {
    adjustTextareaHeight()
  })
}

// 自动调整textarea高度
const adjustTextareaHeight = () => {
  if (!messageTextarea.value || isDragging.value) return

  // 使用requestAnimationFrame优化性能
  requestAnimationFrame(() => {
    if (!messageTextarea.value) return

    // 重置高度以获取正确的scrollHeight
    messageTextarea.value.style.height = 'auto'

    // 计算新高度（scrollHeight + 拖拽区域高度16px）
    const scrollHeight = messageTextarea.value.scrollHeight
    const newHeight = Math.max(minHeight, Math.min(maxHeight, scrollHeight + 16))

    // 只更新响应式变量
    textareaHeight.value = newHeight
  })
}

// 开始拖拽
const startDragging = (event: MouseEvent) => {
  event.preventDefault()
  isDragging.value = true
  dragStartY.value = event.clientY
  dragStartHeight.value = textareaHeight.value

  // 添加全局事件监听
  document.addEventListener('mousemove', handleDragging, { passive: true })
  document.addEventListener('mouseup', stopDragging)

  // 防止文本选择
  document.body.style.userSelect = 'none'
}

// 处理拖拽（使用requestAnimationFrame优化）
const handleDragging = (event: MouseEvent) => {
  if (!isDragging.value) return

  // 取消之前的动画帧
  if (animationFrameId.value) {
    cancelAnimationFrame(animationFrameId.value)
  }

  // 使用requestAnimationFrame确保流畅的动画
  animationFrameId.value = requestAnimationFrame(() => {
    // 向上拖拽（deltaY为负）增加高度，向下拖拽（deltaY为正）减少高度
    const deltaY = event.clientY - dragStartY.value
    const newHeight = Math.max(minHeight, Math.min(maxHeight, dragStartHeight.value - deltaY))

    // 只更新响应式变量，让Vue处理DOM更新
    textareaHeight.value = newHeight
  })
}

// 停止拖拽
const stopDragging = () => {
  isDragging.value = false

  // 取消动画帧
  if (animationFrameId.value) {
    cancelAnimationFrame(animationFrameId.value)
    animationFrameId.value = null
  }

  // 移除全局事件监听
  document.removeEventListener('mousemove', handleDragging)
  document.removeEventListener('mouseup', stopDragging)

  // 恢复文本选择
  document.body.style.userSelect = ''
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

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
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
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
