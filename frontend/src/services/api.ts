import axios, { AxiosInstance, AxiosResponse } from 'axios'
import { useAuthStore } from '@/stores/auth'

// 创建axios实例
const api: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    const token = authStore.token
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error) => {
    const authStore = useAuthStore()
    
    if (error.response?.status === 401) {
      // Token过期或无效，清除认证信息并跳转到登录页
      authStore.logout()
      window.location.href = '/login'
    }
    
    return Promise.reject(error)
  }
)

export default api
