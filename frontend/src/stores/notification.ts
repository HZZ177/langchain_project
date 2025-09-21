import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title?: string
  message: string
  duration?: number
  persistent?: boolean
}

export interface ModalOptions {
  title?: string
  message: string
  confirmText?: string
  cancelText?: string
  type?: 'confirm' | 'alert'
  onConfirm?: () => void | Promise<void>
  onCancel?: () => void
}

export const useNotificationStore = defineStore('notification', () => {
  // 通知列表
  const notifications = ref<Notification[]>([])
  
  // 模态框状态
  const modalVisible = ref(false)
  const modalOptions = ref<ModalOptions | null>(null)

  // 添加通知
  const addNotification = (notification: Omit<Notification, 'id'>) => {
    const id = Date.now().toString() + Math.random().toString(36).substr(2, 9)
    const newNotification: Notification = {
      id,
      duration: 4000, // 默认4秒
      ...notification,
      // 确保duration有有效值
      duration: notification.duration !== undefined ? notification.duration : 4000
    }
    
    notifications.value.push(newNotification)

    // 注意：自动移除逻辑现在由Notification组件处理
    // 这样可以确保有正确的隐藏动画

    return id
  }

  // 移除通知
  const removeNotification = (id: string) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  // 清空所有通知
  const clearNotifications = () => {
    notifications.value = []
  }

  // 显示成功消息
  const success = (message: string, title?: string, duration?: number) => {
    const notification: any = {
      type: 'success',
      title,
      message
    }

    // 只有当duration有明确值时才设置
    if (duration !== undefined) {
      notification.duration = duration
    }

    return addNotification(notification)
  }

  // 显示错误消息
  const error = (message: string, title?: string, duration?: number) => {
    const notification: any = {
      type: 'error',
      title,
      message
    }

    // 错误消息默认显示6秒
    notification.duration = duration !== undefined ? duration : 6000

    return addNotification(notification)
  }

  // 显示警告消息
  const warning = (message: string, title?: string, duration?: number) => {
    const notification: any = {
      type: 'warning',
      title,
      message
    }

    // 只有当duration有明确值时才设置
    if (duration !== undefined) {
      notification.duration = duration
    }

    return addNotification(notification)
  }

  // 显示信息消息
  const info = (message: string, title?: string, duration?: number) => {
    const notification: any = {
      type: 'info',
      title,
      message
    }

    // 只有当duration有明确值时才设置
    if (duration !== undefined) {
      notification.duration = duration
    }

    return addNotification(notification)
  }

  // 显示确认对话框
  const confirm = (options: ModalOptions): Promise<boolean> => {
    return new Promise((resolve) => {
      modalOptions.value = {
        type: 'confirm',
        confirmText: '确定',
        cancelText: '取消',
        ...options,
        onConfirm: async () => {
          try {
            if (options.onConfirm) {
              await options.onConfirm()
            }
            modalVisible.value = false
            resolve(true)
          } catch (error) {
            resolve(false)
          }
        },
        onCancel: () => {
          if (options.onCancel) {
            options.onCancel()
          }
          modalVisible.value = false
          resolve(false)
        }
      }
      modalVisible.value = true
    })
  }

  // 显示警告对话框
  const alert = (options: ModalOptions): Promise<void> => {
    return new Promise((resolve) => {
      modalOptions.value = {
        type: 'alert',
        confirmText: '确定',
        ...options,
        onConfirm: async () => {
          try {
            if (options.onConfirm) {
              await options.onConfirm()
            }
            modalVisible.value = false
            resolve()
          } catch (error) {
            resolve()
          }
        }
      }
      modalVisible.value = true
    })
  }

  // 关闭模态框
  const closeModal = () => {
    modalVisible.value = false
    modalOptions.value = null
  }

  return {
    // 状态
    notifications,
    modalVisible,
    modalOptions,
    
    // 通知方法
    addNotification,
    removeNotification,
    clearNotifications,
    success,
    error,
    warning,
    info,
    
    // 模态框方法
    confirm,
    alert,
    closeModal
  }
})
