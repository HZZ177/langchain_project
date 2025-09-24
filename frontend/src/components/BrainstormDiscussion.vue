<template>
  <div class="brainstorm-discussion max-h-full overflow-y-auto">
    <!-- 讨论主题/背景信息 -->
    <div class="topic-section">
      <div class="topic-header">
        <h3>讨论主题</h3>
        <div class="topic-meta">
          <span class="meta-item">
            模型A: {{ discussionData.config?.model_a || 'GPT-4' }}
          </span>
          <span class="meta-item">
            模型B: {{ discussionData.config?.model_b || 'Claude-3' }}
          </span>
          <span class="meta-item">
            {{ discussionData.config?.style === 'collaborative' ? '协作式' : '辩论式' }}
          </span>
        </div>
      </div>
      <div class="topic-content">
        {{ displayTopic }}
      </div>
    </div>

    <!-- 聊天式对话 -->
    <div class="chat-container">
      <template v-for="round in discussionData.rounds" :key="round.round">
        <!-- 轮次指示器 -->
        <div class="round-indicator">
          <div class="round-badge">
            第 {{ round.round }} 轮讨论
          </div>
        </div>

        <!-- 模型A发言 -->
        <ChatMessage
          :message="{
            message_type: 'assistant',
            content: round.modelA.content,
            timestamp: new Date().toISOString()
          }"
          :is-streaming="round.modelA.isStreaming"
          :is-waiting="!round.modelA.content && !round.modelA.isStreaming"
          :is-model-a="true"
          :model-name="discussionData.config?.model_a || 'GPT-4'"
          :thinking-text="'模型A思考中...'"
          :waiting-text="'等待模型A发言...'"
        />

        <!-- 模型B发言 -->
        <ChatMessage
          :message="{
            message_type: 'assistant',
            content: round.modelB.content,
            timestamp: new Date().toISOString()
          }"
          :is-streaming="round.modelB.isStreaming"
          :is-waiting="!round.modelB.content && !round.modelB.isStreaming"
          :is-model-b="true"
          :model-name="discussionData.config?.model_b || 'Claude-3'"
          :thinking-text="'模型B思考中...'"
          :waiting-text="'等待模型B发言...'"
        />
      </template>
    </div>

    <!-- 讨论总结 -->
    <template v-if="discussionData.summary">
      <!-- 总结指示器 -->
      <div class="summary-indicator">
        <div class="summary-badge">
          💡 讨论总结
        </div>
      </div>

      <!-- 总结内容 -->
      <ChatMessage
        :message="{
          message_type: 'assistant',
          content: discussionData.summary,
          timestamp: new Date().toISOString()
        }"
        :show-header="false"
      />
    </template>

    <!-- 讨论完成指示 -->
    <div v-if="discussionData.isComplete" class="completion-section">
      <div class="completion-badge">
        讨论已完成，共进行了 {{ discussionData.rounds.length }} 轮讨论
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import ChatMessage from './ChatMessage.vue'

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

interface BrainstormDiscussionData {
  topic: string
  config?: DiscussionConfig
  rounds: DiscussionRound[]
  summary?: string
  isComplete: boolean
}

const props = defineProps<{
  discussionData: BrainstormDiscussionData
}>()

// 计算显示的主题
const displayTopic = computed(() => {
  if (props.discussionData.topic) {
    return props.discussionData.topic
  }
  return '等待主题初始化...'
})


</script>

<style scoped>
.brainstorm-discussion {
  max-width: 100%;
  margin: 0 auto;
  /* 确保组件内容在容器内滚动 */
  max-height: 100%;
  overflow-y: auto;
  /* 自定义滚动条样式 */
  scrollbar-width: thin;
  scrollbar-color: #e2e8f0 transparent;
}

.brainstorm-discussion::-webkit-scrollbar {
  width: 4px;
}

.brainstorm-discussion::-webkit-scrollbar-track {
  background: transparent;
}

.brainstorm-discussion::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 2px;
}

.brainstorm-discussion::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}

/* 讨论主题样式 */
.topic-section {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.topic-header h3 {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.topic-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.meta-item {
  background: #e2e8f0;
  color: #64748b;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.topic-content {
  background: white;
  padding: 16px;
  border-radius: 8px;
  border-left: 3px solid #3b82f6;
  font-size: 15px;
  line-height: 1.6;
  color: #374151;
}

/* 聊天容器 */
.chat-container {
  position: relative;
}

/* 轮次指示器 */
.round-indicator {
  text-align: center;
  margin: 24px 0 16px 0;
}

.round-badge {
  display: inline-block;
  background: #f1f5f9;
  color: #64748b;
  padding: 6px 16px;
  border-radius: 12px;
  font-weight: 500;
  font-size: 13px;
  border: 1px solid #e2e8f0;
}

/* 总结指示器样式 */
.summary-indicator {
  text-align: center;
  margin: 32px 0 16px 0;
}

.summary-badge {
  display: inline-block;
  background: #fef3c7;
  color: #92400e;
  padding: 8px 20px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 14px;
  border: 1px solid #fbbf24;
}

/* 完成指示样式 */
.completion-section {
  text-align: center;
  margin-top: 20px;
}

.completion-badge {
  display: inline-block;
  background: #f0fdf4;
  color: #166534;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 13px;
  border: 1px solid #bbf7d0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .topic-section {
    padding: 16px;
  }

  .topic-meta {
    flex-direction: column;
    gap: 6px;
  }

  .meta-item {
    align-self: flex-start;
  }
}

/* 内容样式增强 */
.content-text :deep(h1),
.content-text :deep(h2),
.content-text :deep(h3),
.content-text :deep(h4),
.content-text :deep(h5),
.content-text :deep(h6) {
  margin: 16px 0 8px 0;
  font-weight: 600;
  color: #1e293b;
}

.content-text :deep(p) {
  margin: 8px 0;
  line-height: 1.7;
}

.content-text :deep(ul),
.content-text :deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
}

.content-text :deep(li) {
  margin: 4px 0;
}

.content-text :deep(code) {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.content-text :deep(pre) {
  background: #f8fafc;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 12px 0;
  border: 1px solid #e2e8f0;
}

.content-text :deep(blockquote) {
  border-left: 4px solid #e2e8f0;
  margin: 12px 0;
  padding-left: 16px;
  color: #64748b;
  font-style: italic;
}

.content-text :deep(strong) {
  font-weight: 600;
  color: #1e293b;
}

.content-text :deep(em) {
  font-style: italic;
}
</style>
