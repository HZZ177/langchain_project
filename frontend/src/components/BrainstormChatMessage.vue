<template>
  <div class="brainstorm-message">
    <!-- 讨论开始信息 -->
    <div v-if="message.metadata?.discussion_phase === 'start'" class="discussion-start">
      <div class="start-header">
        <h3>🎯 双模型头脑风暴讨论</h3>
        <div class="discussion-info">
          <span class="info-item">
            <strong>模型A:</strong> {{ message.metadata.model_a }}
          </span>
          <span class="info-item">
            <strong>模型B:</strong> {{ message.metadata.model_b }}
          </span>
          <span class="info-item">
            <strong>讨论轮数:</strong> {{ message.metadata.max_rounds }}轮
          </span>
          <span class="info-item">
            <strong>讨论风格:</strong> {{ message.metadata.style === 'collaborative' ? '协作式' : '辩论式' }}
          </span>
        </div>
      </div>
      <div class="topic-content" v-html="formatContent(message.content)"></div>
    </div>

    <!-- 模型发言开始 -->
    <div v-else-if="message.metadata?.discussion_phase?.includes('_start')" class="model-start">
      <div class="model-header" :class="getModelClass(message.metadata.discussion_phase)">
        <div v-html="formatContent(message.content)"></div>
      </div>
    </div>

    <!-- 模型发言内容 -->
    <div v-else-if="message.metadata?.discussion_phase?.includes('_speaking')" class="model-speaking">
      <div class="model-content" :class="getModelClass(message.metadata.discussion_phase)">
        <div v-html="formatContent(message.content)"></div>
      </div>
    </div>

    <!-- 总结开始 -->
    <div v-else-if="message.metadata?.discussion_phase === 'summary_start'" class="summary-start">
      <div class="summary-header">
        <div v-html="formatContent(message.content)"></div>
      </div>
    </div>

    <!-- 总结内容 -->
    <div v-else-if="message.metadata?.discussion_phase === 'summary'" class="summary-content">
      <div class="summary-text">
        <div v-html="formatContent(message.content)"></div>
      </div>
    </div>

    <!-- 讨论完成 -->
    <div v-else-if="message.metadata?.discussion_phase === 'complete'" class="discussion-complete">
      <div class="complete-info">
        <p>✅ 讨论已完成，共进行了 {{ message.metadata.total_rounds }} 轮讨论</p>
      </div>
    </div>

    <!-- 普通内容（分隔符等） -->
    <div v-else class="normal-content">
      <div v-html="formatContent(message.content)"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  message: {
    content: string
    metadata?: {
      discussion_phase?: string
      model_a?: string
      model_b?: string
      max_rounds?: number
      style?: string
      round?: number
      total_rounds?: number
    }
  }
}>()

// 格式化消息内容
const formatContent = (content: string) => {
  if (!content) return ''

  // 简单的文本格式化，保持换行
  return content.replace(/\n/g, '<br>')
}

// 获取模型样式类
const getModelClass = (phase: string) => {
  if (phase.includes('model_a')) {
    return 'model-a'
  } else if (phase.includes('model_b')) {
    return 'model-b'
  }
  return ''
}
</script>

<style scoped>
.brainstorm-message {
  margin-bottom: 16px;
}

/* 讨论开始样式 */
.discussion-start {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.start-header h3 {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 600;
}

.discussion-info {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 12px;
}

.info-item {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
}

.topic-content {
  background: rgba(255, 255, 255, 0.1);
  padding: 12px;
  border-radius: 8px;
  border-left: 4px solid rgba(255, 255, 255, 0.3);
}

/* 模型发言开始样式 */
.model-start {
  margin: 16px 0 8px 0;
}

.model-header {
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
}

.model-header.model-a {
  background: #e3f2fd;
  color: #1565c0;
  border-left: 4px solid #2196f3;
}

.model-header.model-b {
  background: #f3e5f5;
  color: #7b1fa2;
  border-left: 4px solid #9c27b0;
}

/* 模型发言内容样式 */
.model-speaking {
  margin-bottom: 8px;
}

.model-content {
  padding: 12px 16px;
  border-radius: 8px;
  line-height: 1.6;
}

.model-content.model-a {
  background: #f8f9ff;
  border-left: 3px solid #2196f3;
  margin-left: 12px;
}

.model-content.model-b {
  background: #faf8ff;
  border-left: 3px solid #9c27b0;
  margin-left: 12px;
}

/* 总结样式 */
.summary-start {
  margin: 20px 0 8px 0;
}

.summary-header {
  background: #fff3e0;
  color: #e65100;
  padding: 8px 16px;
  border-radius: 8px;
  border-left: 4px solid #ff9800;
  font-weight: 600;
  font-size: 16px;
}

.summary-content {
  margin-bottom: 8px;
}

.summary-text {
  background: #fffbf0;
  padding: 12px 16px;
  border-radius: 8px;
  border-left: 3px solid #ff9800;
  margin-left: 12px;
  line-height: 1.6;
}

/* 讨论完成样式 */
.discussion-complete {
  background: #e8f5e8;
  color: #2e7d32;
  padding: 12px 16px;
  border-radius: 8px;
  border-left: 4px solid #4caf50;
  text-align: center;
  margin: 16px 0;
}

.complete-info p {
  margin: 0;
  font-weight: 500;
}

/* 普通内容样式 */
.normal-content {
  color: #666;
  font-size: 14px;
  text-align: center;
  margin: 8px 0;
}

/* Markdown内容样式 */
.brainstorm-message :deep(h1),
.brainstorm-message :deep(h2),
.brainstorm-message :deep(h3),
.brainstorm-message :deep(h4),
.brainstorm-message :deep(h5),
.brainstorm-message :deep(h6) {
  margin: 16px 0 8px 0;
  font-weight: 600;
}

.brainstorm-message :deep(p) {
  margin: 8px 0;
  line-height: 1.6;
}

.brainstorm-message :deep(ul),
.brainstorm-message :deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
}

.brainstorm-message :deep(li) {
  margin: 4px 0;
}

.brainstorm-message :deep(code) {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.brainstorm-message :deep(pre) {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 12px 0;
}

.brainstorm-message :deep(blockquote) {
  border-left: 4px solid #ddd;
  margin: 12px 0;
  padding-left: 16px;
  color: #666;
  font-style: italic;
}

.brainstorm-message :deep(strong) {
  font-weight: 600;
}

.brainstorm-message :deep(em) {
  font-style: italic;
}
</style>
