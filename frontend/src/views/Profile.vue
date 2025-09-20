<template>
  <div class="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md mx-auto">
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-2xl font-bold text-gray-900 mb-6">用户信息</h2>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">用户名</label>
            <p class="mt-1 text-sm text-gray-900">{{ authStore.user?.username }}</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">邮箱</label>
            <p class="mt-1 text-sm text-gray-900">{{ authStore.user?.email }}</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">账号类型</label>
            <p class="mt-1 text-sm text-gray-900">
              {{ authStore.user?.is_admin ? '管理员' : '普通用户' }}
            </p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">注册时间</label>
            <p class="mt-1 text-sm text-gray-900">
              {{ formatDate(authStore.user?.created_at) }}
            </p>
          </div>
        </div>

        <div class="mt-6 flex space-x-3">
          <router-link
            to="/chat"
            class="btn-primary"
          >
            返回聊天
          </router-link>
          
          <button
            @click="handleLogout"
            class="btn-secondary"
          >
            退出登录
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

const formatDate = (dateString?: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}
</script>
