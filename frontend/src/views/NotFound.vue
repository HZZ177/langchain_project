<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full text-center">
      <div>
        <h1 class="text-9xl font-bold text-gray-300">404</h1>
        <h2 class="mt-4 text-3xl font-bold text-gray-900">页面未找到</h2>
        <p class="mt-2 text-gray-600">抱歉，您访问的页面不存在。</p>
      </div>
      
      <div class="mt-8">
        <router-link
          to="/chat"
          class="btn-primary"
        >
          返回首页
        </router-link>
      </div>
    </div>
  </div>
</template>
