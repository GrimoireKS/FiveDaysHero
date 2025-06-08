# 固定事件系统简介

## 概述

固定事件系统为《五日勇者》游戏提供预定义的故事事件，这些事件在特定时间必定发生，为游戏提供基础的叙事框架。

## 核心特性

- **内部使用**：仅供LLM推演时使用，不对玩家暴露
- **时间精确**：基于 `TimeOfDay` 枚举的15个时间段
- **自动集成**：自动融入游戏行动处理流程
- **配置驱动**：通过JSON文件管理事件内容

## 文件结构

```
backend/
├── resources/events/
│   └── fixed_events.json          # 事件配置文件
├── services/
│   └── fixed_events_service.py    # 事件服务
├── models/
│   └── common.py                   # 时间枚举定义
└── test_fixed_events.py           # 测试脚本
```

## 事件配置

编辑 `resources/events/fixed_events.json` 来管理固定事件：

```json
[
  {
    "event_time": "D1Morning",
    "event_description": "村庄的钟声响起，标志着新的一天开始..."
  },
  {
    "event_time": "D5Evening",
    "event_description": "命运的时刻终于到来..."
  }
]
```

## 时间格式

使用 `D{天数}{时段}` 格式：
- `D1Morning` - 第1天上午
- `D2Afternoon` - 第2天下午  
- `D3Evening` - 第3天晚上
- ... 以此类推到 `D5Evening`

## 工作原理

1. **自动加载**：服务启动时自动加载配置文件
2. **LLM集成**：在处理玩家行动时，自动将当天的固定事件信息添加到LLM提示中
3. **AI处理**：AI会自然地将固定事件融入到游戏叙述中
4. **透明执行**：玩家感受到的是连贯的故事，而不会意识到某些事件是预定义的

## 测试验证

运行测试脚本验证功能：

```bash
cd backend
python test_fixed_events.py
```

## 注意事项

- 固定事件不对外提供API接口
- 事件描述应该简洁明了，为AI提供叙事指导
- 修改配置文件后需要重启服务
- 事件时间必须使用有效的 `TimeOfDay` 枚举值

## 设计理念

固定事件系统的设计遵循"隐形引导"原则：
- 为游戏提供稳定的故事骨架
- 不限制玩家的自由行动
- 通过AI自然融入，保持沉浸感
- 确保每次游戏都有一致的核心体验
