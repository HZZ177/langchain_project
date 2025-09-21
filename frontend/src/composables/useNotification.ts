import { useNotificationStore } from '@/stores/notification'
import type { ModalOptions } from '@/stores/notification'

export function useNotification() {
  const notificationStore = useNotificationStore()

  // 成功消息
  const success = (message: string, title?: string, duration?: number) => {
    return notificationStore.success(message, title, duration)
  }

  // 错误消息
  const error = (message: string, title?: string, duration?: number) => {
    return notificationStore.error(message, title, duration)
  }

  // 警告消息
  const warning = (message: string, title?: string, duration?: number) => {
    return notificationStore.warning(message, title, duration)
  }

  // 信息消息
  const info = (message: string, title?: string, duration?: number) => {
    return notificationStore.info(message, title, duration)
  }

  // 确认对话框
  const confirm = (options: ModalOptions | string): Promise<boolean> => {
    if (typeof options === 'string') {
      return notificationStore.confirm({ message: options })
    }
    return notificationStore.confirm(options)
  }

  // 警告对话框
  const alert = (options: ModalOptions | string): Promise<void> => {
    if (typeof options === 'string') {
      return notificationStore.alert({ message: options })
    }
    return notificationStore.alert(options)
  }

  // 处理API错误的便捷方法
  const handleError = (error: any, defaultMessage = '操作失败，请稍后重试') => {
    let message = defaultMessage
    
    if (error?.response?.data?.detail) {
      message = error.response.data.detail
    } else if (error?.message) {
      message = error.message
    }
    
    return notificationStore.error(message)
  }

  // 处理成功操作的便捷方法
  const handleSuccess = (message = '操作成功') => {
    return notificationStore.success(message)
  }

  return {
    success,
    error,
    warning,
    info,
    confirm,
    alert,
    handleError,
    handleSuccess
  }
}
