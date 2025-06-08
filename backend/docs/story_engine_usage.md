# 剧情推演引擎使用指南

## 概述

剧情推演引擎是《五日勇者》游戏的核心组件，基于LLM技术实现智能剧情推演。它能够根据当前的游戏状态、角色动作和世界历史，推演出接下来发生的事件，并更新角色状态和世界状态。

## 主要功能

- **智能剧情推演**: 基于LLM分析当前情况，生成合理的剧情发展
- **状态更新**: 自动更新角色属性、关系值、装备等状态
- **世界状态管理**: 更新世界的天气、氛围、地点状态等
- **关系系统**: 跟踪和更新角色间的关系变化
- **事件总结**: 生成简洁的事件摘要和详细的叙述描述

## 核心组件

### 1. 数据模型

#### CharacterAction (角色动作)
```python
from models import CharacterAction

action = CharacterAction(
    character_name="勇者",
    action_description="向村长询问关于魔王的传说",
    location="村庄中心"
)
```

#### LocationInfo (地点信息)
```python
from models import LocationInfo

location = LocationInfo(
    name="村庄中心",
    description="一个宁静的小村庄中心",
    current_characters=["勇者", "村长"],
    special_properties={"atmosphere": "peaceful"}
)
```

#### StoryContext (剧情上下文)
包含完整的剧情推演所需的上下文信息。

#### StoryProgressionResult (推演结果)
包含推演后的所有更新信息。

### 2. 推演引擎

#### StoryEngine 类
核心推演引擎，负责调用LLM进行剧情推演。

#### create_story_progression 函数
便捷函数，简化推演调用过程。

## 使用方法

### 1. 基本使用

```python
from models import CharacterAction, LocationInfo, TimeOfDay
from llm.story_engine import create_story_progression

# 创建地点信息
location = LocationInfo(
    name="村庄中心",
    description="一个宁静的小村庄中心",
    current_characters=["勇者", "村长"],
    special_properties={"atmosphere": "peaceful"}
)

# 创建角色动作
character_actions = [
    CharacterAction(
        character_name="勇者",
        action_description="向村长询问关于魔王的传说",
        location="村庄中心"
    )
]

# 世界历史
world_history = [
    "第一天上午：勇者来到了村庄",
    "村民们对突然出现的勇者感到好奇"
]

# 当前状态
current_world_state = {
    "weather": "晴天",
    "atmosphere": "紧张中带着希望",
    "day": 1
}

current_character_states = {
    "勇者": {
        "stats": {"hp": 100, "mp": 100, "strength": 15},
        "relationship": 0,
        "equipment": {"weapon": "铁剑"},
        "inventory": ["生命药水"]
    }
}

# 执行推演
result = create_story_progression(
    location=location,
    character_actions=character_actions,
    world_history=world_history,
    current_time=TimeOfDay.D1Morning,
    current_world_state=current_world_state,
    current_character_states=current_character_states
)

# 获取结果
print(f"事件总结: {result.event_summary}")
print(f"叙述描述: {result.narrative_description}")
print(f"角色状态更新: {result.updated_character_states}")
print(f"世界状态更新: {result.updated_world_state}")
print(f"关系变化: {result.relationship_changes}")
```

### 2. API 调用

通过HTTP API调用剧情推演：

```bash
curl -X POST http://localhost:5001/api/story/progress \
  -H "Content-Type: application/json" \
  -d '{
    "location": {
      "name": "村庄中心",
      "description": "一个宁静的小村庄中心",
      "current_characters": ["勇者", "村长"],
      "special_properties": {"atmosphere": "peaceful"}
    },
    "character_actions": [
      {
        "character_name": "勇者",
        "action_description": "向村长询问关于魔王的传说",
        "location": "村庄中心"
      }
    ],
    "world_history": [
      "第一天上午：勇者来到了村庄"
    ],
    "current_time": "D1Morning",
    "current_world_state": {
      "weather": "晴天",
      "day": 1
    },
    "current_character_states": {
      "勇者": {
        "stats": {"hp": 100, "strength": 15},
        "relationship": 0
      }
    }
  }'
```

## 配置说明

### 环境变量
确保设置了以下环境变量：
- `ARK_API_KEY`: 火山引擎ARK API密钥

### 提示模板
推演使用的提示模板位于：
`backend/resources/prompts/story_progression_prompt.txt`

可以根据需要修改模板来调整推演风格和输出格式。

## 注意事项

1. **API密钥**: 确保正确配置了火山引擎ARK的API密钥
2. **输入验证**: 推演引擎会验证输入数据的格式和完整性
3. **错误处理**: 推演失败时会抛出详细的错误信息
4. **性能考虑**: LLM调用可能需要几秒钟时间，建议异步处理
5. **状态一致性**: 确保输入的角色状态和世界状态数据一致

## 扩展功能

### 自定义推演规则
可以通过修改提示模板来添加自定义的推演规则和约束。

### 批量推演
支持一次推演多个时间段的剧情发展。

### 结果缓存
可以实现推演结果的缓存机制来提高性能。

## 故障排除

### 常见问题

1. **API调用失败**: 检查网络连接和API密钥配置
2. **JSON解析错误**: 检查LLM返回的格式是否正确
3. **状态更新异常**: 验证输入数据的格式和类型

### 调试模式
设置日志级别为DEBUG可以查看详细的推演过程：

```python
from utils.logger import get_logger
logger = get_logger('llm.story_engine', level='debug')
```
