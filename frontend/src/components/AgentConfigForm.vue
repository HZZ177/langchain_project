<template>
  <div class="h-full flex flex-col">
    <!-- 头部信息 -->
    <div class="flex-shrink-0 p-6 pb-4 border-b border-gray-200">
      <h3 class="text-lg font-medium text-gray-900">{{ agent.name }}</h3>
      <p class="text-sm text-gray-500 mt-1">{{ agent.description }}</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="configLoading" class="flex-1 flex items-center justify-center">
      <div class="flex items-center space-x-2 text-gray-500">
        <svg class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span>加载配置中...</span>
      </div>
    </div>

    <!-- 配置表单 -->
    <div v-else class="flex-1 flex flex-col min-h-0">
      <!-- 根据Agent类型显示不同的配置表单 -->
      <BrainstormAgentConfigForm
        v-if="agent.type === 'brainstorm_agent'"
        :agent-id="agent.id"
        @save="handleSave"
        @cancel="handleCancel"
      />

      <!-- QA Agent配置表单 -->
      <form v-else @submit.prevent="handleSubmit" class="h-full flex flex-col">
        <!-- 表单内容区域 -->
        <div class="flex-1 overflow-y-auto px-6 py-4">
          <div class="space-y-5">
            <!-- 基础配置 -->
            <div class="space-y-4">
              <h4 class="text-md font-medium text-gray-900 border-b border-gray-200 pb-2">基础配置</h4>

            <!-- 模型名称 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                模型名称 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="formData.model_name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="例如: gpt-3.5-turbo"
              />
            </div>

            <!-- 温度 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                温度 ({{ formData.temperature }})
              </label>
              <input
                v-model.number="formData.temperature"
                type="range"
                min="0"
                max="2"
                step="0.1"
                class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
              />
              <div class="flex justify-between text-xs text-gray-500 mt-1">
                <span>0 (确定)</span>
                <span>1 (平衡)</span>
                <span>2 (随机)</span>
              </div>
            </div>

            <!-- 最大Token数 -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <label class="text-sm font-medium text-gray-700">
                  限制最大Token数
                </label>
                <!-- 开关按钮 -->
                <button
                  type="button"
                  @click="enableMaxTokens = !enableMaxTokens"
                  class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  :class="enableMaxTokens ? 'bg-blue-600' : 'bg-gray-200'"
                >
                  <span
                    class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
                    :class="enableMaxTokens ? 'translate-x-6' : 'translate-x-1'"
                  ></span>
                </button>
              </div>

              <!-- 输入框（仅在开关开启时显示） -->
              <div v-if="enableMaxTokens" class="mt-2">
                <input
                  v-model.number="formData.max_tokens"
                  type="number"
                  min="1"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="例如: 2000"
                />
              </div>

              <p class="text-xs text-gray-500 mt-1">
                {{ enableMaxTokens ? '设置生成的最大Token数量' : '无限制模式，让模型自由生成完整回答（推荐）' }}
              </p>
            </div>

            <!-- 对话轮数 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                保留上下文轮数
              </label>
              <input
                v-model.number="formData.max_conversation_rounds"
                type="number"
                min="1"
                max="50"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="例如: 5"
              />
              <p class="text-xs text-gray-500 mt-1">
                设置AI记忆的对话轮数，数值越大消耗的token越多
              </p>
            </div>
          </div>

          <!-- API配置 -->
          <div class="space-y-4">
            <h4 class="text-md font-medium text-gray-900 border-b border-gray-200 pb-2">API配置</h4>

            <!-- API密钥 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                API密钥 <span class="text-red-500">*</span>
              </label>
              <div class="relative">
                <input
                  v-model="formData.api_key"
                  :type="showApiKey ? 'text' : 'password'"
                  required
                  class="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="输入您的API密钥"
                />
                <button
                  type="button"
                  @click="showApiKey = !showApiKey"
                  class="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  <svg v-if="showApiKey" class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                  </svg>
                  <svg v-else class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- API基础URL -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                API基础URL
              </label>
              <input
                v-model="formData.base_url"
                type="url"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="例如: https://api.openai.com/v1"
              />
            </div>
          </div>
        </div>
      </div>


      <!-- 底部固定区域 -->
      <div class="flex-shrink-0 border-t border-gray-200 p-6">
        <!-- 错误提示 -->
        <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-sm text-red-600">{{ error }}</p>
        </div>

        <!-- 操作按钮 -->
        <div class="flex justify-end space-x-4">
        <button
          type="button"
          @click="$emit('cancel')"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          取消
        </button>
        <button
          type="submit"
          :disabled="saving"
          class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="saving" class="flex items-center">
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            保存中...
          </span>
          <span v-else>保存配置</span>
        </button>
        </div>
      </div>
    </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { agentService } from '@/services/agent'
import { useNotification } from '@/composables/useNotification'
import type { Agent } from '@/types'
import BrainstormAgentConfigForm from './BrainstormAgentConfigForm.vue'

const props = defineProps<{
  agent: Agent
  loading?: boolean
}>()

const emit = defineEmits<{
  save: []
  cancel: []
}>()

const notification = useNotification()

// 响应式数据
const configLoading = ref(false)
const saving = ref(false)
const showApiKey = ref(false)
const error = ref('')

// 表单数据
const formData = ref({
  model_name: '',
  temperature: 0.7,
  max_tokens: null,
  api_key: '',
  base_url: '',
  max_conversation_rounds: 5
})

// Token限制开关状态
const enableMaxTokens = ref(false)
// 记住用户上次设置的Token值
const lastMaxTokensValue = ref(2000)

// 加载配置数据
const loadConfig = async () => {
  if (!props.agent) return
  
  configLoading.value = true
  error.value = ''
  
  try {
    const config = await agentService.getAgentConfig(props.agent.id)
    
    // 填充表单数据
    formData.value = {
      model_name: config.model_name || '',
      temperature: config.temperature !== undefined ? config.temperature : 0.7,
      max_tokens: config.max_tokens,
      api_key: config.api_key || '',
      base_url: config.base_url || '',
      max_conversation_rounds: config.max_conversation_rounds !== undefined ? config.max_conversation_rounds : 5
    }

    // 设置Token限制开关状态
    enableMaxTokens.value = config.max_tokens !== null && config.max_tokens !== undefined

    // 如果有具体的Token值，记住它
    if (config.max_tokens !== null && config.max_tokens !== undefined) {
      lastMaxTokensValue.value = config.max_tokens
    }
  } catch (err) {
    error.value = '加载配置失败'
    notification.handleError(err, '加载配置失败')
  } finally {
    configLoading.value = false
  }
}

// 处理BrainstormAgentConfigForm的保存事件
const handleSave = () => {
  emit('save')
}

// 处理BrainstormAgentConfigForm的取消事件
const handleCancel = () => {
  emit('cancel')
}

// 保存配置
const handleSubmit = async () => {
  if (!props.agent) return

  saving.value = true
  error.value = ''

  try {
    // 处理max_tokens值
    const configData = { ...formData.value }
    if (!enableMaxTokens.value) {
      configData.max_tokens = null
    }

    await agentService.updateAgentConfig(props.agent.id, configData)
    emit('save')
  } catch (err) {
    error.value = '保存配置失败'
    notification.handleError(err, '保存配置失败')
  } finally {
    saving.value = false
  }
}

// 监听Token限制开关变化
watch(enableMaxTokens, (newValue) => {
  if (!newValue) {
    // 关闭时，先记住当前值（如果有的话），然后设置为null
    if (formData.value.max_tokens && formData.value.max_tokens > 0) {
      lastMaxTokensValue.value = formData.value.max_tokens
    }
    formData.value.max_tokens = null
  } else {
    // 开启时，使用记住的值
    formData.value.max_tokens = lastMaxTokensValue.value
  }
})

// 监听agent变化，重新加载配置
watch(() => props.agent, loadConfig, { immediate: true })

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.slider::-webkit-slider-thumb {
  appearance: none;
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
}

.slider::-moz-range-thumb {
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: none;
}
</style>
