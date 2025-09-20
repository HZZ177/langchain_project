<template>
  <div class="flex justify-start">
    <div class="max-w-xs lg:max-w-md px-4 py-3 rounded-lg bg-white border border-gray-200 text-gray-900">
      <div class="flex items-center space-x-2">
        <div class="flex space-x-1">
          <div 
            class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
            style="animation-delay: 0ms"
          ></div>
          <div 
            class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
            style="animation-delay: 150ms"
          ></div>
          <div 
            class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
            style="animation-delay: 300ms"
          ></div>
        </div>
        <span class="text-sm text-gray-500">AI正在思考...</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 无需额外的逻辑，纯展示组件
</script>

<style scoped>
@keyframes bounce {
  0%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-8px);
  }
}

.animate-bounce {
  animation: bounce 1.4s infinite ease-in-out;
}
</style>
