<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click="emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-6xl h-[90vh] flex flex-col overflow-hidden" @click.stop>
      <!-- 头部 -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <h2 class="text-xl font-semibold text-gray-900">Agent配置管理</h2>
        <button
          @click="$emit('close')"
          class="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- 主体内容 -->
      <div class="flex flex-1 overflow-hidden">
        <!-- 左侧Agent列表 -->
        <div class="w-1/4 border-r border-gray-200 overflow-y-auto">
          <div class="p-6">
            <h3 class="text-sm font-medium text-gray-700 mb-3">配置管理</h3>
            <div class="space-y-2">
              <!-- 系统配置选项 -->
              <button
                @click="selectSystemConfig()"
                class="w-full text-left p-3 rounded-lg border transition-colors"
                :class="{
                  'border-blue-500 bg-blue-50': selectedConfigType === 'system',
                  'border-gray-200 hover:bg-gray-50': selectedConfigType !== 'system'
                }"
              >
                <div class="flex items-center space-x-3">
                  <div class="flex-shrink-0">
                    <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 truncate">系统配置</p>
                    <p class="text-xs text-gray-500 truncate">管理系统级功能配置</p>
                  </div>
                </div>
              </button>

              <!-- 分隔线 -->
              <div class="border-t border-gray-200 my-3"></div>
              <h4 class="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">Agent配置</h4>

              <!-- Agent列表 -->
              <button
                v-for="agent in agents"
                :key="agent.id"
                @click="selectAgent(agent)"
                class="w-full text-left p-3 rounded-lg border transition-colors"
                :class="{
                  'border-blue-500 bg-blue-50': selectedAgent?.id === agent.id && selectedConfigType === 'agent',
                  'border-gray-200 hover:bg-gray-50': !(selectedAgent?.id === agent.id && selectedConfigType === 'agent')
                }"
              >
                <div class="flex items-center space-x-3">
                  <div class="flex-shrink-0">
                    <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 truncate">{{ agent.name }}</p>
                    <p class="text-xs text-gray-500 truncate">{{ agent.description }}</p>
                  </div>
                </div>
              </button>
            </div>
          </div>
        </div>

        <!-- 右侧配置表单 -->
        <div class="flex-1 flex flex-col min-h-0">
          <!-- 未选择任何配置时的提示 -->
          <div v-if="selectedConfigType === null" class="flex items-center justify-center h-full">
            <div class="text-center text-gray-500">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <p class="mt-2 text-sm">请选择要配置的项目</p>
            </div>
          </div>

          <!-- 系统配置表单 -->
          <SystemConfigForm
            v-else-if="selectedConfigType === 'system'"
            @save="handleSave"
            @cancel="$emit('close')"
          />

          <!-- Agent配置表单 -->
          <AgentConfigForm
            v-else-if="selectedConfigType === 'agent' && selectedAgent"
            :agent="selectedAgent"
            :loading="loading"
            @save="handleSave"
            @cancel="$emit('close')"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import AgentConfigForm from './AgentConfigForm.vue'
import SystemConfigForm from './SystemConfigForm.vue'
import type { Agent } from '@/types'

const props = defineProps<{
  agents: Agent[]
}>()

const emit = defineEmits<{
  close: []
  'config-saved': []
}>()

const selectedAgent = ref<Agent | null>(null)
const selectedConfigType = ref<'system' | 'agent' | null>(null)
const loading = ref(false)

const selectAgent = (agent: Agent) => {
  selectedAgent.value = agent
  selectedConfigType.value = 'agent'
}

const selectSystemConfig = () => {
  selectedAgent.value = null
  selectedConfigType.value = 'system'
}

// 自动选择系统配置
const autoSelectSystemConfig = () => {
  if (!selectedConfigType.value) {
    selectedConfigType.value = 'system'
  }
}

// 监听agents变化，自动选择系统配置
watch(() => props.agents, autoSelectSystemConfig, { immediate: true })

const handleSave = async () => {
  loading.value = true
  try {
    // 配置保存逻辑在AgentConfigForm中处理
    emit('config-saved')
  } finally {
    loading.value = false
  }
}

// ESC键监听
const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    emit('close')
  }
}

// 组件挂载时添加键盘监听
onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

// 组件卸载时移除键盘监听
onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>
