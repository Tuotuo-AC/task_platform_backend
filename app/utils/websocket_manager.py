from fastapi import WebSocket
from typing import Dict, Set
from app.core.redis_client import redis_client

# 管理所有活跃的 WebSocket 连接，支持按用户 ID 添加/移除连接，并向指定用户的所有连接发送消息
class ConnectionManager:
    def __init__(self):
        # 初始化一个空字典，用于存储用户 ID 到其 WebSocket 连接集合的映射
        self.active_connections: Dict[int, Set[WebSocket]] = {}
    # 将一个新的 WebSocket 连接注册到管理器中
    async def connect(self, user_id: int, websocket: WebSocket):
        # 正式建立 WebSocket 连接
        await websocket.accept()
        # 如果该用户还没有任何连接，创建一个空集合
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        # 将当前 websocket 对象添加到用户对应的集合中
        self.active_connections[user_id].add(websocket)
    # 移除一个不再活跃的 WebSocket 连接
    def disconnect(self, user_id: int, websocket: WebSocket):
        # 如果用户存在于字典中，从集合中移除指定的 websocket
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            # 如果移除后该用户的集合变为空，则删除该键，避免残留空集合
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    # 向指定用户的所有活跃 WebSocket 连接发送文本消息
    async def send_personal_message(self, user_id: int, message: str):
        # 检查用户是否有活跃连接
        if user_id in self.active_connections:
            # 遍历该用户的所有连接，尝试发送消息
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                # 如果发送失败（如连接已断开），捕获异常并忽略（pass），继续尝试发送给其他连接。
                except:
                    pass
# 创建一个全局单例，供其他模块使用
manager = ConnectionManager()


#  Redis 订阅转发器listen_redis_and_forward
async def listen_redis_and_forward():
    # 创建订阅对象
    pubsub = redis_client.pubsub()
    # 订阅频道
    pubsub.subscribe("notifications")
    # 循环监听
    for message in pubsub.listen():
        # 过滤消息类型：只处理 type == "message" 的事件（忽略订阅成功等控制消息）
        if message["type"] == "message":
            try:
                # 解析消息
                user_id_str, content = message["data"].split(":", 1)
                # 转换用户 ID为整数
                user_id = int(user_id_str)
                # 将消息推送给该用户的所有 WebSocket 连接
                await manager.send_personal_message(user_id, content)
            except:
                pass