# 游戏会话管理和文件存储系统

## 概述

本系统实现了完整的游戏会话管理和文件存储功能，支持：
- 基于游戏ID的会话管理
- JSON文件持久化存储
- 7天数据保留机制
- 自动清理过期文件
- 原子性文件操作
- 完整的错误处理和日志记录

## 系统架构

### 核心组件

1. **文件存储服务** (`services/file_storage_service.py`)
   - 提供底层文件操作功能
   - 支持原子性写入和安全读取
   - 自动备份和恢复机制

2. **会话管理服务** (`services/session_service.py`)
   - 管理游戏会话的生命周期
   - 验证会话有效性
   - 提供会话统计信息

3. **游戏数据服务** (`services/game_data_service.py`)
   - 高级游戏状态管理
   - 支持增量状态更新
   - 提供游戏逻辑相关操作

4. **清理任务管理器** (`utils/cleanup_tasks.py`)
   - 定时清理过期文件
   - 监控存储使用情况
   - 支持手动清理操作

### 工具模块

1. **文件工具** (`utils/file_utils.py`)
   - 安全的文件操作函数
   - 游戏ID生成和验证
   - 过期文件检测和清理

2. **JSON工具** (`utils/json_utils.py`)
   - 游戏数据序列化/反序列化
   - 元数据管理
   - 数据结构验证

## 目录结构

```
backend/
├── data/                    # 数据存储目录
│   ├── games/              # 游戏会话文件
│   │   ├── game_xxx.json   # 游戏数据文件
│   │   └── ...
│   ├── backups/            # 备份文件
│   │   ├── 2024-01-01/     # 按日期分组的备份
│   │   └── ...
│   └── logs/               # 系统日志
├── services/               # 服务层
│   ├── file_storage_service.py
│   ├── session_service.py
│   └── game_data_service.py
└── utils/                  # 工具模块
    ├── file_utils.py
    ├── json_utils.py
    └── cleanup_tasks.py
```

## API接口

### 会话管理接口

#### 获取会话信息
```
GET /api/game/session/{game_id}
```

#### 获取游戏状态
```
GET /api/game/session/{game_id}/state
```

#### 更新游戏状态
```
PUT /api/game/session/{game_id}/state
Body: {
  "state_updates": {
    "day": 2,
    "player": {"hp": 95}
  }
}
```

#### 列出所有会话
```
GET /api/game/sessions?include_expired=false
```

#### 删除会话
```
DELETE /api/game/session/{game_id}
```

### 世界创建接口（已更新）

#### 创建世界和会话
```
POST /api/world/create
Body: {
  "playerResponse": "我是一个勇敢的战士..."
}

Response: {
  "status": "success",
  "game_id": "game_xxx-xxx-xxx",
  "hero": {...},
  "world": {...},
  "gameState": {...}
}
```

## 使用示例

### 1. 创建新游戏

```python
from services import get_game_data_service

game_data_service = get_game_data_service()

initial_data = {
    "player": {
        "name": "勇者",
        "stats": {"strength": 10, "intelligence": 8}
    },
    "world": {
        "current_day": 1,
        "weather": "晴天"
    }
}

game_id = game_data_service.create_new_game(initial_data)
print(f"游戏ID: {game_id}")
```

### 2. 获取和更新游戏状态

```python
# 获取游戏状态
game_state = game_data_service.get_game_state(game_id)

# 更新游戏状态
state_updates = {
    "day": 2,
    "player": {"hp": 95}
}
success = game_data_service.update_game_state(game_id, state_updates)
```

### 3. 会话管理

```python
from services import get_session_service

session_service = get_session_service()

# 验证会话
is_valid = session_service.validate_session(game_id)

# 获取会话信息
session_info = session_service.get_session_info(game_id)

# 延长会话有效期
session_service.extend_session_expiry(game_id, 7)
```

## 配置说明

### 数据保留策略
- 游戏文件默认保留7天
- 备份文件保留30天
- 日志文件保留7天

### 清理任务时间表
- 每天凌晨2点：清理过期游戏文件
- 每天凌晨3点：清理过期日志文件
- 每天凌晨4点：清理过期备份文件
- 每小时：检查存储使用情况

### 存储限制
- 单个游戏文件建议不超过1MB
- 总存储使用超过100MB时记录警告
- 总存储使用超过500MB时触发紧急清理

## 安全特性

### 文件安全
- 原子性写入（临时文件+重命名）
- 文件锁防止并发冲突
- 游戏ID格式验证防止路径遍历
- 自动备份重要操作

### 数据完整性
- JSON数据结构验证
- 元数据完整性检查
- 过期时间验证
- 错误恢复机制

## 监控和日志

### 日志级别
- DEBUG: 详细操作信息
- INFO: 重要操作记录
- WARNING: 潜在问题提醒
- ERROR: 错误和异常

### 监控指标
- 活跃会话数量
- 存储使用情况
- 清理任务执行情况
- 错误发生频率

## 故障排除

### 常见问题

1. **游戏会话创建失败**
   - 检查数据目录权限
   - 验证初始数据格式
   - 查看错误日志

2. **文件读写错误**
   - 检查磁盘空间
   - 验证文件权限
   - 检查文件锁状态

3. **清理任务不执行**
   - 检查定时任务状态
   - 验证清理任务配置
   - 查看任务调度日志

### 调试工具

运行测试脚本检查系统状态：
```bash
cd backend
python test_session_management.py
```

## 性能优化

### 建议
1. 定期清理过期文件
2. 监控存储使用情况
3. 优化JSON数据结构
4. 使用增量状态更新
5. 合理设置备份策略

### 扩展性
- 支持分布式文件存储
- 可扩展到数据库存储
- 支持多服务器部署
- 可配置的清理策略
