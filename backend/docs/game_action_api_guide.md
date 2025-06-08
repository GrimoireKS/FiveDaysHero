# 游戏行动处理API使用指南

## 概述

游戏行动处理API (`/api/game/action`) 是《五日勇者》游戏的核心接口，负责处理玩家的游戏行动并通过LLM推演游戏世界的变化。

## API接口

### 处理玩家行动

**接口**: `POST /api/game/action`

**请求参数**:
```json
{
  "game_id": "game_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "action": "玩家行动描述（100字以内）"
}
```

**响应格式**:
```json
{
  "status": "success",
  "result": {
    "player_actions": {
      "morning": "上午具体行动描述",
      "afternoon": "下午具体行动描述",
      "evening": "晚上具体行动描述"
    },
    "npc_actions": {
      "npc_id": {
        "morning": "NPC上午行动",
        "afternoon": "NPC下午行动", 
        "evening": "NPC晚上行动"
      }
    },
    "time_progression": {
      "morning": {
        "narrative": "上午时段的详细叙述",
        "events": ["事件1", "事件2"],
        "state_changes": {
          "player": {"hp": 变化值, "mp": 变化值},
          "world": {"weather": "新天气"},
          "relationships": {"npc_id": 关系变化值}
        }
      },
      "afternoon": {...},
      "evening": {...}
    },
    "day_summary": {
      "narrative": "整天的总结叙述",
      "major_events": ["重要事件1", "重要事件2"],
      "achievements": ["成就1", "成就2"],
      "consequences": ["后果1", "后果2"]
    },
    "updated_states": {
      "player": {
        "hp": 最终值,
        "mp": 最终值,
        "其他属性": 最终值
      },
      "world": {
        "current_time": "晚上",
        "weather": "最终天气",
        "其他属性": "最终值"
      },
      "npcs": {
        "npc_id": {
          "relationship": 最终关系值,
          "其他属性": "最终值"
        }
      }
    }
  },
  "updated_game_state": {
    "day": 当前天数,
    "player": {...},
    "world": {...},
    "npc": {...},
    "history": [...]
  },
  "message": "行动处理完成"
}
```

## 使用流程

### 1. 创建游戏会话

首先通过世界创建接口创建游戏：

```bash
curl -X POST http://localhost:5001/api/world/create \
  -H "Content-Type: application/json" \
  -d '{
    "playerResponse": "我是一个勇敢的战士，手持长剑，身穿皮甲..."
  }'
```

响应中会包含 `game_id`，保存此ID用于后续操作。

### 2. 处理玩家行动

使用获得的 `game_id` 处理玩家行动：

```bash
curl -X POST http://localhost:5001/api/game/action \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "game_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "action": "我想在村庄里四处走走，了解一下这个地方的情况，和村民们聊聊天，看看有什么任务可以做。"
  }'
```

### 3. 继续游戏

重复调用行动接口，直到游戏完成（5天）：

```bash
curl -X POST http://localhost:5001/api/game/action \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "game_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", 
    "action": "我要去森林里探险，寻找一些有用的材料和宝物。"
  }'
```

## 前端集成示例

### JavaScript/Vue.js 示例

```javascript
// 游戏行动处理函数
async function processPlayerAction(gameId, action) {
  try {
    const response = await fetch('/api/game/action', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        game_id: gameId,
        action: action
      })
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
      // 处理成功响应
      const actionResult = result.result;
      const updatedGameState = result.updated_game_state;
      
      // 更新UI显示
      updateGameUI(actionResult, updatedGameState);
      
      return result;
    } else {
      // 处理错误
      console.error('行动处理失败:', result.message);
      return null;
    }
  } catch (error) {
    console.error('API调用失败:', error);
    return null;
  }
}

// 更新游戏UI
function updateGameUI(actionResult, gameState) {
  // 显示时段叙述
  const timeProgression = actionResult.time_progression;
  displayTimeProgression(timeProgression);
  
  // 显示一天总结
  const daySummary = actionResult.day_summary;
  displayDaySummary(daySummary);
  
  // 更新玩家状态
  updatePlayerStats(gameState.player);
  
  // 更新世界状态
  updateWorldInfo(gameState.world);
  
  // 更新NPC关系
  updateNPCRelationships(gameState.npc);
}
```

## 错误处理

### 常见错误码

- `400`: 请求参数错误
  - 缺少 `game_id`
  - 缺少 `action`
  - 游戏已完成

- `404`: 游戏会话不存在或已过期

- `500`: 服务器内部错误
  - LLM调用失败
  - 状态更新失败

### 错误响应示例

```json
{
  "status": "error",
  "message": "游戏会话不存在或已过期"
}
```

## 游戏机制说明

### 时段系统

每个游戏日分为三个时段：
- **上午**: 玩家行动的开始
- **下午**: 继续执行计划
- **晚上**: 一天的结束

### 状态管理

游戏维护以下状态：

1. **玩家状态**
   - 基本属性：HP、MP、力量、智力、敏捷、幸运
   - 装备信息
   - 经验和成就

2. **世界状态**
   - 当前天数和时间
   - 天气状况
   - 地点信息

3. **NPC状态**
   - 基本信息
   - 与玩家的关系值
   - 行动历史

### 关系系统

NPC关系值范围：-100 到 +100
- 负值：敌对关系
- 0：中性关系
- 正值：友好关系

## 性能考虑

### 响应时间

- 正常情况下，API响应时间为 5-15 秒
- 复杂行动可能需要更长时间
- 建议前端显示加载状态

### 并发限制

- 每个游戏会话同时只能处理一个行动
- 建议前端禁用重复提交

## 调试和测试

### 测试脚本

运行测试脚本验证功能：

```bash
cd backend
python test_game_action.py
```

### 日志查看

查看详细日志：

```bash
tail -f backend/logs/service.log
```

### 手动测试

使用curl命令进行手动测试：

```bash
# 创建游戏
curl -X POST http://localhost:5001/api/world/create \
  -H "Content-Type: application/json" \
  -d '{"playerResponse": "测试勇者"}'

# 处理行动
curl -X POST http://localhost:5001/api/game/action \
  -H "Content-Type: application/json" \
  -d '{"game_id": "your_game_id", "action": "探索村庄"}'
```

## 最佳实践

1. **行动描述**
   - 保持在100字以内
   - 描述具体明确
   - 避免过于复杂的计划

2. **错误处理**
   - 始终检查响应状态
   - 提供用户友好的错误信息
   - 实现重试机制

3. **状态同步**
   - 及时更新本地游戏状态
   - 定期验证会话有效性
   - 处理会话过期情况

4. **用户体验**
   - 显示处理进度
   - 提供取消操作选项
   - 保存游戏历史记录
