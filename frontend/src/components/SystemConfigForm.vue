<template>
  <div class="h-full flex flex-col">
    <!-- 头部信息 -->
    <div class="flex-shrink-0 p-6 pb-4 border-b border-gray-200">
      <h3 class="text-lg font-medium text-gray-900">系统配置</h3>
      <p class="text-sm text-gray-500 mt-1">管理系统级功能配置</p>
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
    <form v-else @submit.prevent="handleSubmit" class="h-full flex flex-col">
      <!-- 表单内容区域 -->
      <div class="flex-1 overflow-y-auto px-6 py-4">
        <div class="space-y-6">
          <!-- 标题生成配置 -->
          <div class="space-y-4">
            <h4 class="text-md font-medium text-gray-900 border-b border-gray-200 pb-2">会话标题自动生成</h4>

            <!-- 功能开关 -->
            <div class="flex items-center justify-between">
              <div>
                <label class="block text-sm font-medium text-gray-700">
                  启用自动标题生成
                </label>
                <p class="text-xs text-gray-500 mt-1">
                  在用户对话达到指定轮数后自动生成会话标题
                </p>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input
                  v-model="formData.enabled"
                  type="checkbox"
                  class="sr-only peer"
                />
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <!-- 模型配置 -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <!-- 模型名称 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  模型名称 <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="formData.model"
                  type="text"
                  required
                  :disabled="!formData.enabled"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:text-gray-500"
                  placeholder="例如: gpt-3.5-turbo"
                />
              </div>

              <!-- 触发轮数 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  触发轮数
                </label>
                <input
                  v-model.number="formData.trigger_rounds"
                  type="number"
                  min="1"
                  max="10"
                  :disabled="!formData.enabled"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:text-gray-500"
                  placeholder="例如: 2"
                />
                <p class="text-xs text-gray-500 mt-1">
                  用户与AI完成几轮对话后触发标题生成
                </p>
              </div>
            </div>

            <!-- API配置 -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                    :disabled="!formData.enabled"
                    class="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:text-gray-500"
                    placeholder="sk-..."
                  />
                  <button
                    type="button"
                    @click="showApiKey = !showApiKey"
                    :disabled="!formData.enabled"
                    class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 disabled:text-gray-300"
                  >
                    <svg v-if="showApiKey" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <svg v-else class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
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
                  :disabled="!formData.enabled"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:text-gray-500"
                  placeholder="例如: https://api.openai.com/v1"
                />
              </div>
            </div>

            <!-- 高级参数 -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <!-- 温度参数 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  温度参数
                </label>
                <input
                  v-model.number="formData.temperature"
                  type="number"
                  min="0"
                  max="2"
                  step="0.1"
                  :disabled="!formData.enabled"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:text-gray-500"
                  placeholder="0.3"
                />
                <p class="text-xs text-gray-500 mt-1">
                  控制输出的随机性，建议使用较低值确保标题稳定
                </p>
              </div>

              <!-- 最大Token数 -->
              <div>
                <div class="flex items-center justify-between mb-1">
                  <label class="block text-sm font-medium text-gray-700">
                    最大Token数
                  </label>
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input
                      v-model="enableMaxTokens"
                      type="checkbox"
                      class="sr-only peer"
                      :disabled="!formData.enabled"
                    />
                    <div class="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600 peer-disabled:opacity-50"></div>
                    <span class="ml-2 text-xs text-gray-600">启用限制</span>
                  </label>
                </div>
                <input
                  v-model.number="maxTokensValue"
                  type="number"
                  min="10"
                  max="200"
                  :disabled="!formData.enabled || !enableMaxTokens"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:text-gray-500"
                  placeholder="50"
                />
                <p class="text-xs text-gray-500 mt-1">
                  {{ enableMaxTokens ? '限制生成标题的最大长度' : '不限制Token数量（推荐）' }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="px-6 py-2">
        <div class="bg-red-50 border border-red-200 rounded-lg p-3">
          <div class="flex">
            <svg class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div class="ml-3">
              <p class="text-sm text-red-800">{{ error }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部按钮 -->
      <div class="flex-shrink-0 px-6 py-4 border-t border-gray-200">
        <div class="flex justify-end space-x-3">
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
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { systemService } from '@/services/system'
import { useNotification } from '@/composables/useNotification'

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

// Token限制相关
const enableMaxTokens = ref(false)
const maxTokensValue = ref(50)

// 表单数据
const formData = ref({
  enabled: true,
  model: 'gpt-3.5-turbo',
  api_key: '',
  base_url: 'https://x666.me/v1',
  temperature: 0.3,
  max_tokens: null as number | null,
  trigger_rounds: 2
})

// 加载配置
const loadConfig = async () => {
  configLoading.value = true
  error.value = ''

  try {
    const config = await systemService.getTitleGenerationConfig()

    // 更新表单数据
    formData.value = {
      enabled: config.enabled,
      model: config.model,
      api_key: config.api_key,
      base_url: config.base_url,
      temperature: config.temperature,
      max_tokens: config.max_tokens,
      trigger_rounds: config.trigger_rounds
    }

    // 设置Token限制开关状态
    enableMaxTokens.value = config.max_tokens !== null && config.max_tokens !== undefined

    // 如果有具体的Token值，记住它
    if (config.max_tokens !== null && config.max_tokens !== undefined) {
      maxTokensValue.value = config.max_tokens
    }
  } catch (err) {
    error.value = '加载配置失败'
    notification.handleError(err, '加载配置失败')
  } finally {
    configLoading.value = false
  }
}

// 保存配置
const handleSubmit = async () => {
  saving.value = true
  error.value = ''

  try {
    // 处理max_tokens值
    const configData = { ...formData.value }
    if (enableMaxTokens.value) {
      configData.max_tokens = maxTokensValue.value
    } else {
      configData.max_tokens = null
    }

    await systemService.updateTitleGenerationConfig(configData)
    notification.success('配置保存成功')
    emit('save')
  } catch (err) {
    error.value = '保存配置失败'
    notification.handleError(err, '保存配置失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadConfig()
})
</script>
