<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <router-view />

    <!-- 通知容器 -->
    <NotificationContainer />

    <!-- 模态对话框 -->
    <Modal />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import NotificationContainer from '@/components/ui/NotificationContainer.vue'
import Modal from '@/components/ui/Modal.vue'

const authStore = useAuthStore()

onMounted(async () => {
  // 初始化认证状态
  await authStore.initAuth()
})
</script>
