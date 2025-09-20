import api from './api'
import type { User, LoginForm, RegisterForm, Token } from '@/types'

export const authService = {
  // 用户登录
  async login(loginForm: LoginForm): Promise<Token> {
    const response = await api.post('/auth/login', loginForm)
    return response.data
  },

  // 用户注册
  async register(registerForm: RegisterForm): Promise<User> {
    const response = await api.post('/auth/register', registerForm)
    return response.data
  },

  // 获取当前用户信息
  async getCurrentUser(): Promise<User> {
    const response = await api.get('/auth/me')
    return response.data
  },

  // 刷新Token
  async refreshToken(): Promise<Token> {
    const response = await api.post('/auth/refresh')
    return response.data
  },

  // 用户登出
  async logout(): Promise<void> {
    await api.post('/auth/logout')
  },
}
