<template>
  <div class="flex-1 flex flex-col">
    <!-- 表单内容区域 -->
    <div class="flex-1 overflow-y-auto px-6">
      <div class="space-y-5">
        <!-- 错误提示 -->
        <div v-if="error" class="p-3 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-sm text-red-600">{{ error }}</p>
        </div>

        <!-- 双模型配置 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- 模型A配置 -->
          <div class="space-y-4">
            <h4 class="text-md font-medium text-gray-900 border-b border-gray-200 pb-2">模型A配置</h4>

            <!-- 模型名称 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                模型名称 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="formData.model_a_name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="例如: gpt-4"
              />
            </div>

            <!-- 温度 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                温度 ({{ formData.model_a_temperature }})
              </label>
              <input
                v-model.number="formData.model_a_temperature"
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

            <!-- API密钥 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                API密钥 <span class="text-red-500">*</span>
              </label>
              <div class="relative">
                <input
                  v-model="formData.model_a_api_key"
                  :type="showApiKeyA ? 'text' : 'password'"
                  required
                  class="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="输入模型A的API密钥"
                />
                <button
                  type="button"
                  @click="showApiKeyA = !showApiKeyA"
                  class="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  <svg v-if="showApiKeyA" class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                v-model="formData.model_a_base_url"
                type="url"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="例如: https://api.openai.com/v1"
              />
            </div>

            <!-- 系统提示词 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                系统提示词
              </label>
              <textarea
                v-model="formData.model_a_system_prompt"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="留空使用默认提示词"
              ></textarea>
            </div>
          </div>

          <!-- 模型B配置 -->
          <div class="space-y-4">
            <h4 class="text-md font-medium text-gray-900 border-b border-gray-200 pb-2">模型B配置</h4>

            <!-- 模型名称 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                模型名称 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="formData.model_b_name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="例如: claude-3-sonnet"
              />
            </div>

            <!-- 温度 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                温度 ({{ formData.model_b_temperature }})
              </label>
              <input
                v-model.number="formData.model_b_temperature"
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

            <!-- API密钥 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                API密钥 <span class="text-red-500">*</span>
              </label>
              <div class="relative">
                <input
                  v-model="formData.model_b_api_key"
                  :type="showApiKeyB ? 'text' : 'password'"
                  required
                  class="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="输入模型B的API密钥"
                />
                <button
                  type="button"
                  @click="showApiKeyB = !showApiKeyB"
                  class="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  <svg v-if="showApiKeyB" class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                v-model="formData.model_b_base_url"
                type="url"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="例如: https://api.anthropic.com/v1"
              />
            </div>

            <!-- 系统提示词 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                系统提示词
              </label>
              <textarea
                v-model="formData.model_b_system_prompt"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="留空使用默认提示词"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- 讨论配置 -->
        <div class="space-y-4">
          <h4 class="text-md font-medium text-gray-900 border-b border-gray-200 pb-2">讨论配置</h4>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- 最大讨论轮数 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                最大讨论轮数
              </label>
              <input
                v-model.number="formData.max_discussion_rounds"
                type="number"
                min="1"
                max="10"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="例如: 5"
              />
              <p class="text-xs text-gray-500 mt-1">
                设置两个模型的最大讨论轮数 (1-10轮)
              </p>
            </div>

            <!-- 讨论风格 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                讨论风格
              </label>
              <select
                v-model="formData.discussion_style"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="collaborative">协作式</option>
                <option value="debate">辩论式</option>
              </select>
              <p class="text-xs text-gray-500 mt-1">
                协作式：建设性合作；辩论式：观点对抗
              </p>
            </div>
          </div>

          <!-- 启用讨论总结 -->
          <div>
            <div class="flex items-center justify-between mb-2">
              <label class="text-sm font-medium text-gray-700">
                启用讨论总结
              </label>
              <!-- 开关按钮 -->
              <button
                type="button"
                @click="formData.enable_summary = !formData.enable_summary"
                class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                :class="formData.enable_summary ? 'bg-blue-600' : 'bg-gray-200'"
              >
                <span
                  class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
                  :class="formData.enable_summary ? 'translate-x-6' : 'translate-x-1'"
                ></span>
              </button>
            </div>

            <!-- 总结提示词（仅在开关开启时显示） -->
            <div v-if="formData.enable_summary" class="mt-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                总结提示词
              </label>
              <textarea
                v-model="formData.summary_prompt"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="留空使用默认总结提示词"
              ></textarea>
            </div>

            <p class="text-xs text-gray-500 mt-1">
              {{ formData.enable_summary ? '讨论结束后生成总结' : '关闭总结功能，直接结束讨论' }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部固定区域 -->
    <div class="flex-shrink-0 border-t border-gray-200 p-6">
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
          @click="handleSubmit"
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { agentService } from '@/services/agent'
import { useNotification } from '@/composables/useNotification'

const props = defineProps<{
  agentId: number
}>()

const emit = defineEmits<{
  save: []
  cancel: []
}>()

const notification = useNotification()

// 响应式数据
const saving = ref(false)
const showApiKeyA = ref(false)
const showApiKeyB = ref(false)
const error = ref('')

// 表单数据
const formData = ref({
  model_a_name: 'gpt-4',
  model_a_temperature: 0.7,
  model_a_api_key: '',
  model_a_base_url: 'https://api.openai.com/v1',
  model_a_system_prompt: '',
  
  model_b_name: 'claude-3-sonnet',
  model_b_temperature: 0.7,
  model_b_api_key: '',
  model_b_base_url: 'https://api.anthropic.com/v1',
  model_b_system_prompt: '',
  
  max_discussion_rounds: 5,
  discussion_style: 'collaborative',
  enable_summary: true,
  summary_prompt: ''
})

// 加载配置
const loadConfig = async () => {
  try {
    const config = await agentService.getAgentConfig(props.agentId)
    
    // 更新表单数据
    Object.keys(formData.value).forEach(key => {
      if (config[key] !== undefined) {
        formData.value[key] = config[key]
      }
    })
  } catch (err) {
    error.value = '加载配置失败'
    console.error('加载配置失败:', err)
  }
}

// 保存配置
const handleSubmit = async () => {
  saving.value = true
  error.value = ''

  try {
    await agentService.updateAgentConfig(props.agentId, formData.value)
    notification.success('配置保存成功')
    emit('save')
  } catch (err) {
    error.value = '保存配置失败'
    notification.error('保存配置失败')
    console.error('保存配置失败:', err)
  } finally {
    saving.value = false
  }
}

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
