import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginForm, RegisterForm, Token } from '@/types'
import { authService } from '@/services/auth'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const loading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.is_admin || false)

  // 设置认证信息
  const setAuth = (authData: Token, userData: User) => {
    token.value = authData.access_token
    refreshToken.value = authData.refresh_token
    user.value = userData

    // 保存到localStorage
    localStorage.setItem('access_token', authData.access_token)
    localStorage.setItem('refresh_token', authData.refresh_token)
  }

  // 清除认证信息
  const clearAuth = () => {
    token.value = null
    refreshToken.value = null
    user.value = null

    // 清除localStorage
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  // 登录
  const login = async (loginForm: LoginForm) => {
    loading.value = true
    try {
      // 第一步：获取token
      const tokenData = await authService.login(loginForm)

      // 第二步：先设置token，确保后续请求能携带认证信息
      token.value = tokenData.access_token
      refreshToken.value = tokenData.refresh_token
      localStorage.setItem('access_token', tokenData.access_token)
      localStorage.setItem('refresh_token', tokenData.refresh_token)

      // 第三步：获取用户信息（此时请求会自动携带token）
      const userData = await authService.getCurrentUser()

      // 第四步：设置用户信息
      user.value = userData

      return { success: true }
    } catch (error: any) {
      // 如果出错，清除可能已设置的token
      clearAuth()
      return {
        success: false,
        message: error.response?.data?.detail || '登录失败',
      }
    } finally {
      loading.value = false
    }
  }

  // 注册
  const register = async (registerForm: RegisterForm) => {
    loading.value = true
    try {
      await authService.register(registerForm)
      return { success: true }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '注册失败',
      }
    } finally {
      loading.value = false
    }
  }

  // 登出
  const logout = async () => {
    try {
      if (token.value) {
        await authService.logout()
      }
    } catch (error) {
      console.error('登出请求失败:', error)
    } finally {
      clearAuth()
    }
  }

  // 获取当前用户信息
  const fetchCurrentUser = async () => {
    if (!token.value) return false

    try {
      const userData = await authService.getCurrentUser()
      user.value = userData
      return true
    } catch (error) {
      console.error('获取用户信息失败:', error)
      clearAuth()
      return false
    }
  }

  // 刷新Token
  const refreshAccessToken = async () => {
    if (!refreshToken.value) return false

    try {
      const tokenData = await authService.refreshToken()
      token.value = tokenData.access_token
      refreshToken.value = tokenData.refresh_token

      localStorage.setItem('access_token', tokenData.access_token)
      localStorage.setItem('refresh_token', tokenData.refresh_token)
      
      return true
    } catch (error) {
      console.error('刷新Token失败:', error)
      clearAuth()
      return false
    }
  }

  // 初始化认证状态
  const initAuth = async () => {
    if (token.value) {
      const success = await fetchCurrentUser()
      if (!success) {
        // 如果获取用户信息失败，尝试刷新Token
        await refreshAccessToken()
      }
    }
  }

  return {
    // 状态
    user,
    token,
    refreshToken,
    loading,
    
    // 计算属性
    isAuthenticated,
    isAdmin,
    
    // 方法
    login,
    register,
    logout,
    fetchCurrentUser,
    refreshAccessToken,
    initAuth,
    setAuth,
    clearAuth,
  }
})
