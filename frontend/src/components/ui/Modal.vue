<template>
  <Teleport to="body">
    <Transition
      enter-active-class="ease-out duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="ease-in duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="notificationStore.modalVisible"
        class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity z-50"
        @click="handleBackdropClick"
      />
    </Transition>

    <Transition
      enter-active-class="ease-out duration-300"
      enter-from-class="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
      enter-to-class="opacity-100 translate-y-0 sm:scale-100"
      leave-active-class="ease-in duration-200"
      leave-from-class="opacity-100 translate-y-0 sm:scale-100"
      leave-to-class="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
    >
      <div
        v-if="notificationStore.modalVisible && notificationStore.modalOptions"
        class="fixed inset-0 z-50 overflow-y-auto"
      >
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <div class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg">
            <div class="bg-white px-4 pb-4 pt-5 sm:p-6 sm:pb-4">
              <div class="sm:flex sm:items-start">
                <div
                  v-if="notificationStore.modalOptions.type === 'confirm'"
                  class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10"
                >
                  <svg
                    class="h-6 w-6 text-red-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke-width="1.5"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
                    />
                  </svg>
                </div>
                <div
                  v-else
                  class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-blue-100 sm:mx-0 sm:h-10 sm:w-10"
                >
                  <svg
                    class="h-6 w-6 text-blue-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke-width="1.5"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z"
                    />
                  </svg>
                </div>
                <div class="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left">
                  <h3
                    v-if="notificationStore.modalOptions.title"
                    class="text-base font-semibold leading-6 text-gray-900"
                  >
                    {{ notificationStore.modalOptions.title }}
                  </h3>
                  <div class="mt-2">
                    <p class="text-sm text-gray-500">
                      {{ notificationStore.modalOptions.message }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
              <button
                @click="handleConfirm"
                type="button"
                class="inline-flex w-full justify-center rounded-md px-3 py-2 text-sm font-semibold text-white shadow-sm sm:ml-3 sm:w-auto"
                :class="[
                  notificationStore.modalOptions.type === 'confirm'
                    ? 'bg-red-600 hover:bg-red-500'
                    : 'bg-primary-600 hover:bg-primary-500'
                ]"
              >
                {{ notificationStore.modalOptions.confirmText || '确定' }}
              </button>
              <button
                v-if="notificationStore.modalOptions.type === 'confirm'"
                @click="handleCancel"
                type="button"
                class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
              >
                {{ notificationStore.modalOptions.cancelText || '取消' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { useNotificationStore } from '@/stores/notification'

const notificationStore = useNotificationStore()

const handleConfirm = () => {
  if (notificationStore.modalOptions?.onConfirm) {
    notificationStore.modalOptions.onConfirm()
  } else {
    notificationStore.closeModal()
  }
}

const handleCancel = () => {
  if (notificationStore.modalOptions?.onCancel) {
    notificationStore.modalOptions.onCancel()
  } else {
    notificationStore.closeModal()
  }
}

const handleBackdropClick = () => {
  if (notificationStore.modalOptions?.type === 'confirm') {
    handleCancel()
  } else {
    handleConfirm()
  }
}

// ESC键关闭
const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && notificationStore.modalVisible) {
    if (notificationStore.modalOptions?.type === 'confirm') {
      handleCancel()
    } else {
      handleConfirm()
    }
  }
}

// 监听键盘事件
document.addEventListener('keydown', handleKeydown)
</script>
