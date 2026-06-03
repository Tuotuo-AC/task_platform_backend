from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.security import decode_token
from app.utils.websocket_manager import manager

router = APIRouter(tags=["Notifications"])

# WebSocket端点
@router.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    # 获取并验证token
    token = websocket.query_params.get("token")
    # 关闭无效连接
    if not token:
        await websocket.close(code=1008)
        return
    # 解码并验证token
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        await websocket.close(code=1008)
        return
    # 提取用户ID并转换为整数
    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=1008)
        return
    user_id = int(user_id)
    # 注册连接
    await manager.connect(user_id, websocket)
    # 保持连接并监听客户端消息
    try:
        while True:
            await websocket.receive_text()  # 保持连接
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)