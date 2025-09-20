"""
WebSocket连接管理器
"""
from typing import Dict, Set, Optional
from fastapi import WebSocket
import json
import asyncio


class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, Set[str]] = {}  # user_id -> session_ids
        self.session_users: Dict[str, str] = {}  # session_id -> user_id
    
    async def connect(self, websocket: WebSocket, session_id: str, user_id: str):
        """建立WebSocket连接"""
        await websocket.accept()
        
        # 如果该会话已有连接，先断开旧连接
        if session_id in self.active_connections:
            try:
                old_websocket = self.active_connections[session_id]
                await old_websocket.close()
            except Exception:
                pass
        
        # 建立新连接
        self.active_connections[session_id] = websocket
        self.session_users[session_id] = user_id
        
        # 更新用户会话映射
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = set()
        self.user_sessions[user_id].add(session_id)
        
        print(f"WebSocket连接已建立: session_id={session_id}, user_id={user_id}")
    
    def disconnect(self, session_id: str):
        """断开WebSocket连接"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        
        if session_id in self.session_users:
            user_id = self.session_users[session_id]
            del self.session_users[session_id]
            
            # 更新用户会话映射
            if user_id in self.user_sessions:
                self.user_sessions[user_id].discard(session_id)
                if not self.user_sessions[user_id]:
                    del self.user_sessions[user_id]
        
        print(f"WebSocket连接已断开: session_id={session_id}")
    
    async def send_message(self, session_id: str, message: dict) -> bool:
        """发送消息到特定会话"""
        if session_id not in self.active_connections:
            return False
        
        try:
            websocket = self.active_connections[session_id]
            await websocket.send_text(json.dumps(message, ensure_ascii=False))
            return True
        except Exception as e:
            print(f"发送消息失败: session_id={session_id}, error={e}")
            # 连接可能已断开，清理连接
            self.disconnect(session_id)
            return False
    
    async def broadcast_to_user(self, user_id: str, message: dict):
        """广播消息到用户的所有会话"""
        if user_id not in self.user_sessions:
            return
        
        # 复制会话ID集合，避免在迭代过程中修改
        session_ids = self.user_sessions[user_id].copy()
        
        for session_id in session_ids:
            await self.send_message(session_id, message)
    
    def get_active_sessions(self) -> Dict[str, str]:
        """获取所有活跃会话"""
        return self.session_users.copy()
    
    def get_user_sessions(self, user_id: str) -> Set[str]:
        """获取用户的所有活跃会话"""
        return self.user_sessions.get(user_id, set()).copy()
    
    def is_session_active(self, session_id: str) -> bool:
        """检查会话是否活跃"""
        return session_id in self.active_connections
    
    def get_session_user(self, session_id: str) -> Optional[str]:
        """获取会话对应的用户ID"""
        return self.session_users.get(session_id)
    
    async def ping_all_connections(self):
        """向所有连接发送ping消息"""
        if not self.active_connections:
            return
        
        ping_message = {"type": "ping", "data": {}}
        
        # 复制连接字典，避免在迭代过程中修改
        connections = self.active_connections.copy()
        
        for session_id in connections:
            await self.send_message(session_id, ping_message)
    
    async def cleanup_inactive_connections(self):
        """清理非活跃连接"""
        inactive_sessions = []
        
        for session_id, websocket in self.active_connections.items():
            try:
                # 尝试发送ping消息检查连接状态
                await websocket.ping()
            except Exception:
                inactive_sessions.append(session_id)
        
        # 清理非活跃连接
        for session_id in inactive_sessions:
            self.disconnect(session_id)
        
        if inactive_sessions:
            print(f"清理了 {len(inactive_sessions)} 个非活跃连接")


# 全局WebSocket管理器实例
websocket_manager = WebSocketManager()
