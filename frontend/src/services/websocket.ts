import type { WebSocketMessage, UserMessage, AgentResponse, ErrorMessage } from '@/types'

export class WebSocketService {
  private ws: WebSocket | null = null
  private sessionId: string | null = null
  private token: string | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private messageHandlers: Map<string, (data: any) => void> = new Map()

  constructor() {
    this.setupDefaultHandlers()
  }

  private setupDefaultHandlers() {
    this.onMessage('connection_established', (data) => {
      console.log('WebSocket连接已建立:', data)
      this.reconnectAttempts = 0
    })

    this.onMessage('error', (data: ErrorMessage['data']) => {
      console.error('WebSocket错误:', data)
    })

    this.onMessage('pong', () => {
      console.log('收到pong响应')
    })
  }

  connect(sessionId: string, token: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.sessionId = sessionId
      this.token = token

      const wsUrl = `ws://localhost:8000/api/v1/ws/${sessionId}?token=${encodeURIComponent(token)}`
      
      try {
        this.ws = new WebSocket(wsUrl)

        this.ws.onopen = () => {
          console.log('WebSocket连接已打开')
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('解析WebSocket消息失败:', error)
          }
        }

        this.ws.onclose = (event) => {
          console.log('WebSocket连接已关闭:', event.code, event.reason)
          this.handleReconnect()
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket连接错误:', error)
          reject(error)
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  private handleMessage(message: WebSocketMessage) {
    const handler = this.messageHandlers.get(message.type)
    if (handler) {
      handler(message.data)
    } else {
      console.log('未处理的消息类型:', message.type, message.data)
    }
  }

  private handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts && this.sessionId && this.token) {
      this.reconnectAttempts++
      console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
      
      setTimeout(() => {
        this.connect(this.sessionId!, this.token!)
          .catch(error => {
            console.error('重连失败:', error)
          })
      }, this.reconnectDelay * this.reconnectAttempts)
    }
  }

  sendMessage(message: UserMessage | { type: string; data: any }) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.error('WebSocket未连接')
    }
  }

  sendUserMessage(content: string, extra_data?: Record<string, any>) {
    const message: UserMessage = {
      type: 'user_message',
      data: {
        content,
        extra_data,
      },
    }
    this.sendMessage(message)
  }

  ping() {
    this.sendMessage({
      type: 'ping',
      data: {},
    })
  }

  onMessage(type: string, handler: (data: any) => void) {
    this.messageHandlers.set(type, handler)
  }

  offMessage(type: string) {
    this.messageHandlers.delete(type)
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.sessionId = null
    this.token = null
    this.reconnectAttempts = 0
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}

// 全局WebSocket服务实例
export const websocketService = new WebSocketService()
