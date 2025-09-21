<template>
  <div
    aria-live="assertive"
    class="fixed inset-0 flex items-end justify-center px-4 py-6 pointer-events-none sm:p-6 sm:items-start sm:justify-end z-50"
  >
    <div class="w-full flex flex-col items-center space-y-4 sm:items-end">
      <Notification
        v-for="notification in notificationStore.notifications"
        :key="notification.id"
        :notification="notification"
        @close="notificationStore.removeNotification(notification.id)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useNotificationStore } from '@/stores/notification'
import Notification from './Notification.vue'

const notificationStore = useNotificationStore()
</script>
