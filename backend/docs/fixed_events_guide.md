# 固定事件系统使用指南

## 概述

固定事件系统是《五日勇者》游戏中的重要组成部分，用于管理在特定时间必定发生的事件。这些事件为游戏提供了基础的故事框架和世界观背景。

## 系统架构

### 核心组件

1. **时间枚举** (`models/common.py`)
   - 定义了游戏中的15个时间段（5天 × 3个时段）
   - 格式：`D{天数}{时段}` (如 `D1Morning`, `D2Afternoon`)

2. **固定事件服务** (`services/fixed_events_service.py`)
   - 管理固定事件的加载、查询和格式化
   - 提供与游戏系统的集成接口

3. **事件配置文件** (`resources/events/fixed_events.json`)
   - JSON格式的事件配置
   - 包含事件时间和描述

## 时间枚举定义

```python
class TimeOfDay(Enum):
    D1Morning = "D1Morning"      # 第1天上午
    D1Afternoon = "D1Afternoon"  # 第1天下午
    D1Evening = "D1Evening"      # 第1天晚上
    D2Morning = "D2Morning"      # 第2天上午
    # ... 以此类推到 D5Evening
```

## 配置文件格式

固定事件配置文件位于 `backend/resources/events/fixed_events.json`：

```json
[
  {
    "event_time": "D1Morning",
    "event_description": "村庄的钟声响起，标志着新的一天开始..."
  },
  {
    "event_time": "D1Evening", 
    "event_description": "夜幕降临，村庄的酒馆里传来阵阵欢声笑语..."
  }
]
```

### 配置字段说明

- `event_time`: 事件发生时间，必须是有效的 `TimeOfDay` 枚举值
- `event_description`: 事件描述，用于游戏叙述中

## 内部服务接口

固定事件系统仅供内部使用，不对外提供API接口。主要通过 `FixedEventsService` 类提供服务。

## 服务使用示例

### 内部服务调用

```python
from services import get_fixed_events_service
from models.common import TimeOfDay

# 获取固定事件服务
fixed_events_service = get_fixed_events_service()

# 检查特定时间是否有事件
has_event = fixed_events_service.has_fixed_event(TimeOfDay.D1Morning)

# 获取事件描述
event_desc = fixed_events_service.get_fixed_event(TimeOfDay.D1Morning)

# 获取第1天的所有事件
day1_events = fixed_events_service.get_fixed_events_for_day(1)

# 格式化事件用于LLM提示
formatted_events = fixed_events_service.format_fixed_events_for_prompt(1)
```

## 游戏集成

### LLM提示集成

固定事件会自动集成到游戏行动处理的LLM提示中：

1. **系统提示更新**: 告知AI必须处理固定事件
2. **用户提示包含**: 当前天的固定事件信息
3. **自动格式化**: 事件信息格式化为易读文本

### 游戏流程集成

在 `GameActionService` 中：

```python
# 获取当前天的固定事件
current_day = game_state.get('day', 1)
fixed_events_info = self.fixed_events_service.format_fixed_events_for_prompt(current_day)

# 包含在LLM提示中
prompt = template.format(
    # ... 其他参数
    fixed_events_info=fixed_events_info,
    # ...
)
```

## 事件设计原则

### 内容设计

1. **渐进式紧张感**: 从第1天的平静到第5天的高潮
2. **世界观一致性**: 所有事件符合奇幻世界设定
3. **玩家引导**: 事件暗示可能的行动方向
4. **情感层次**: 营造不同的情感氛围

### 时间分布

- **第1天**: 介绍世界背景，建立基调
- **第2-3天**: 发展冲突，增加神秘感
- **第4天**: 危机升级，紧张感达到高峰
- **第5天**: 最终决战，命运时刻

## 配置管理

### 添加新事件

1. 编辑 `resources/events/fixed_events.json`
2. 添加新的事件对象
3. 确保 `event_time` 使用正确的枚举值
4. 重启服务或调用服务的重新加载方法

### 修改现有事件

1. 直接编辑配置文件中的 `event_description`
2. 保持 `event_time` 不变
3. 重启服务生效

### 验证配置

使用测试脚本验证配置：

```bash
cd backend
python test_fixed_events.py
```

## 调试和监控

### 日志记录

固定事件服务会记录以下日志：

- 配置文件加载状态
- 事件查询操作
- 格式化操作
- 错误和警告

### 常见问题

1. **配置文件格式错误**
   - 检查JSON语法
   - 验证字段名称

2. **无效的时间枚举**
   - 确保使用正确的枚举值
   - 检查大小写和格式

3. **事件未生效**
   - 检查配置是否重新加载
   - 验证LLM提示是否包含事件信息

## 扩展功能

### 条件事件

未来可以扩展支持条件事件：

```json
{
  "event_time": "D2Morning",
  "event_description": "...",
  "conditions": {
    "player_hp": ">50",
    "npc_relationship": {"village_chief": ">0"}
  }
}
```

### 随机事件池

可以为每个时段配置多个可选事件：

```json
{
  "event_time": "D1Morning",
  "event_pool": [
    {"weight": 0.7, "description": "常见事件"},
    {"weight": 0.3, "description": "稀有事件"}
  ]
}
```

## 最佳实践

1. **保持简洁**: 事件描述应该简洁明了
2. **避免冲突**: 确保事件与玩家可能的行动不冲突
3. **测试验证**: 定期测试事件的效果和影响
4. **版本控制**: 对配置文件进行版本控制
5. **备份配置**: 定期备份事件配置文件
