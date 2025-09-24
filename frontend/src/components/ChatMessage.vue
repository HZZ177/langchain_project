<template>
  <div class="chat-message" :class="messageClass">
    <div class="message-container">
      <!-- 头像 -->
      <div class="avatar-container">
        <div class="avatar" :class="avatarClass">
          <span v-if="message.message_type === 'user'">{{ userInitial }}</span>
          <span v-else-if="isModelA">A</span>
          <span v-else-if="isModelB">B</span>
          <span v-else>AI</span>
        </div>
      </div>

      <!-- 消息气泡 -->
      <div class="message-bubble" :class="bubbleClass">
        <!-- 消息头部（仅AI消息显示） -->
        <div v-if="message.message_type !== 'user' && showHeader" class="message-header">
          <div class="sender-info">
            <span class="sender-name">{{ senderName }}</span>
            <span v-if="modelDetail" class="model-detail">{{ modelDetail }}</span>
          </div>
          <div v-if="timestamp" class="timestamp">{{ formatTime(timestamp) }}</div>
        </div>

        <!-- 消息内容 -->
        <div class="message-content" :class="{ 'streaming': isStreaming }">
          <div v-if="content" class="content-text" v-html="formatContent(content)"></div>
          <div v-else-if="isStreaming" class="thinking-indicator">
            <div class="thinking-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <span class="thinking-text">{{ thinkingText }}</span>
          </div>
          <div v-else-if="isWaiting" class="waiting-indicator">{{ waitingText }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'

interface Props {
  message: {
    message_type: 'user' | 'assistant'
    content: string
    timestamp?: string
  }
  isStreaming?: boolean
  isWaiting?: boolean
  isModelA?: boolean
  isModelB?: boolean
  modelName?: string
  showHeader?: boolean
  thinkingText?: string
  waitingText?: string
}

const props = withDefaults(defineProps<Props>(), {
  isStreaming: false,
  isWaiting: false,
  isModelA: false,
  isModelB: false,
  showHeader: true,
  thinkingText: '思考中...',
  waitingText: '等待发言...'
})

// 计算属性
const messageClass = computed(() => ({
  'message-user': props.message.message_type === 'user',
  'message-assistant': props.message.message_type === 'assistant',
  'message-model-a': props.isModelA,
  'message-model-b': props.isModelB
}))

const avatarClass = computed(() => ({
  'avatar-user': props.message.message_type === 'user',
  'avatar-assistant': props.message.message_type === 'assistant',
  'avatar-model-a': props.isModelA,
  'avatar-model-b': props.isModelB
}))

const bubbleClass = computed(() => ({
  'bubble-user': props.message.message_type === 'user',
  'bubble-assistant': props.message.message_type === 'assistant',
  'bubble-model-a': props.isModelA,
  'bubble-model-b': props.isModelB
}))

const userInitial = computed(() => {
  // 这里可以从用户信息中获取首字母，暂时使用默认值
  return 'U'
})

const senderName = computed(() => {
  if (props.isModelA) return props.modelName || 'GPT-4'
  if (props.isModelB) return props.modelName || 'Claude-3'
  return 'AI助手'
})

const modelDetail = computed(() => {
  if (props.isModelA) return '模型A'
  if (props.isModelB) return '模型B'
  return null
})

const content = computed(() => props.message.content)
const timestamp = computed(() => props.message.timestamp)

// 方法
const formatContent = (text: string) => {
  if (!text) return ''
  
  // 清理多余的换行和空格
  let cleaned = text.replace(/\n{3,}/g, '\n\n').trim()
  
  // 转换Markdown
  try {
    return marked(cleaned, {
      breaks: true,
      gfm: true
    })
  } catch (error) {
    console.error('Markdown parsing error:', error)
    return cleaned.replace(/\n/g, '<br>')
  }
}

const formatTime = (timestamp: string) => {
  if (!timestamp) return ''
  try {
    return new Date(timestamp).toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return ''
  }
}
</script>

<style scoped>
/* 消息容器 */
.chat-message {
  margin-bottom: 16px;
  display: flex;
}

.message-user {
  justify-content: flex-end;
}

.message-assistant,
.message-model-a {
  justify-content: flex-start;
}

.message-model-b {
  justify-content: flex-end;
}

.message-container {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  max-width: 75%;
}

.message-user .message-container,
.message-model-b .message-container {
  flex-direction: row-reverse;
}

/* 头像样式 */
.avatar-container {
  flex-shrink: 0;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: white;
}

.avatar-user {
  background: #3b82f6;
}

.avatar-assistant {
  background: #64748b;
}

.avatar-model-a {
  background: #3b82f6;
}

.avatar-model-b {
  background: #64748b;
}

/* 消息气泡 */
.message-bubble {
  background: white;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  min-width: 120px;
}

.message-bubble:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.bubble-user {
  background: white;
  border: 1px solid #3b82f6;
  border-left: 4px solid #3b82f6;
}

.bubble-assistant {
  border-left: 4px solid #64748b;
}

.bubble-model-a {
  border-left: 4px solid #3b82f6;
}

.bubble-model-b {
  border: 1px solid #64748b;
  border-left: 4px solid #64748b;
}

/* 消息头部 */
.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  font-size: 12px;
}

.bubble-model-a .message-header {
  background: #f0f9ff;
}

.sender-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.sender-name {
  font-weight: 500;
  color: #374151;
}

.model-detail {
  color: #64748b;
  font-size: 11px;
}

.timestamp {
  color: #9ca3af;
  font-size: 11px;
}

/* 消息内容 */
.message-content {
  padding: 12px 16px;
  min-height: 40px;
}

.message-content {
  color: #374151;
}

.content-text {
  line-height: 1.6;
  font-size: 14px;
}

.content-text {
  color: #374151;
}

/* 思考和等待指示器 */
.thinking-indicator,
.waiting-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;
  color: #9ca3af;
  font-style: italic;
  font-size: 13px;
}

.thinking-dots {
  display: flex;
  gap: 3px;
  margin-right: 6px;
}

.thinking-dots span {
  width: 4px;
  height: 4px;
  background: #cbd5e1;
  border-radius: 50%;
  animation: thinking 1.4s infinite ease-in-out both;
}

.thinking-dots span:nth-child(1) { animation-delay: -0.32s; }
.thinking-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes thinking {
  0%, 80%, 100% {
    transform: scale(0);
  } 40% {
    transform: scale(1);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .message-container {
    max-width: 90%;
  }

  .avatar {
    width: 32px;
    height: 32px;
    font-size: 12px;
  }

  .message-content {
    padding: 10px 12px;
  }
}
</style>
