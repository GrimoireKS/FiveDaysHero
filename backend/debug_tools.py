#!/usr/bin/env python3
"""
调试工具集
提供各种调试和诊断功能
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from services import get_game_data_service, get_session_service, get_game_action_service
from utils.logger import get_logger

# 设置调试日志级别
logging.basicConfig(level=logging.DEBUG)
logger = get_logger(__name__)


def enable_debug_logging():
    """启用详细调试日志"""
    # 设置所有相关模块的日志级别为DEBUG
    modules = [
        'services.game_data_service',
        'services.session_service', 
        'services.game_action_service',
        'services.file_storage_service',
        'utils.file_utils',
        'utils.json_utils',
        'llm.chat'
    ]
    
    for module in modules:
        module_logger = logging.getLogger(module)
        module_logger.setLevel(logging.DEBUG)
    
    print("✓ 调试日志已启用")


def create_debug_game() -> Optional[str]:
    """创建用于调试的测试游戏"""
    print("=== 创建调试游戏 ===")
    
    game_data_service = get_game_data_service()
    
    # 创建简单的测试数据
    initial_data = {
        "player": {
            "name": "调试勇者",
            "gender": "男",
            "profession": "战士",
            "age": 20,
            "stats": {
                "hp": 100,
                "mp": 100,
                "strength": 10,
                "intelligence": 8,
                "agility": 12,
                "luck": 6
            },
            "equipment": {
                "hands": ["木剑"]
            }
        },
        "world": {
            "current_day": 1,
            "current_time": "上午",
            "weather": "晴天",
            "locations": {
                "village": {
                    "name": "测试村庄",
                    "description": "用于调试的村庄"
                }
            }
        },
        "npc": {
            "test_npc": {
                "name": "测试NPC",
                "profession": "村民",
                "age": 30,
                "gender": "女",
                "relationship": 0,
                "stats": {
                    "strength": 5,
                    "intelligence": 10
                }
            }
        },
        "history": [],
        "events": []
    }
    
    print("创建游戏...")
    game_id = game_data_service.create_new_game(initial_data)
    
    if game_id:
        print(f"✓ 调试游戏创建成功: {game_id}")
        return game_id
    else:
        print("✗ 调试游戏创建失败")
        return None


def debug_game_state(game_id: str):
    """调试游戏状态"""
    print(f"\n=== 调试游戏状态: {game_id} ===")
    
    game_data_service = get_game_data_service()
    session_service = get_session_service()
    
    # 验证会话
    print("1. 验证会话...")
    is_valid = session_service.validate_session(game_id)
    print(f"   会话有效性: {is_valid}")
    
    if not is_valid:
        print("   会话无效，停止调试")
        return
    
    # 获取会话数据
    print("2. 获取会话数据...")
    session_data = session_service.get_session_data(game_id)
    if session_data:
        print(f"   会话数据键: {list(session_data.keys())}")
        
        metadata = session_data.get('metadata', {})
        print(f"   创建时间: {metadata.get('created_at', '未知')}")
        print(f"   最后访问: {metadata.get('last_accessed', '未知')}")
        print(f"   过期时间: {metadata.get('expires_at', '未知')}")
    else:
        print("   获取会话数据失败")
        return
    
    # 获取游戏状态
    print("3. 获取游戏状态...")
    game_state = game_data_service.get_game_state(game_id)
    if game_state:
        print(f"   游戏状态键: {list(game_state.keys())}")
        print(f"   当前天数: {game_state.get('day', '未知')}")
        
        player = game_state.get('player', {})
        print(f"   玩家姓名: {player.get('name', '未知')}")
        print(f"   玩家HP: {player.get('stats', {}).get('hp', '未知')}")
        
        world = game_state.get('world', {})
        print(f"   当前时间: {world.get('current_time', '未知')}")
        print(f"   天气: {world.get('weather', '未知')}")
        
        npcs = game_state.get('npc', {})
        print(f"   NPC数量: {len(npcs)}")
    else:
        print("   获取游戏状态失败")


def debug_action_processing(game_id: str, action: str = "我想在村庄里走走看看"):
    """调试行动处理"""
    print(f"\n=== 调试行动处理: {game_id} ===")
    print(f"行动: {action}")
    
    game_action_service = get_game_action_service()
    
    print("开始处理行动...")
    result = game_action_service.process_player_action(game_id, action)
    
    if result:
        print("✓ 行动处理成功")
        print(f"结果键: {list(result.keys())}")
        
        # 显示玩家行动分解
        player_actions = result.get('player_actions', {})
        if player_actions:
            print("玩家行动分解:")
            for time_period, action_desc in player_actions.items():
                print(f"  {time_period}: {action_desc[:50]}...")
        
        # 显示一天总结
        day_summary = result.get('day_summary', {})
        if day_summary.get('narrative'):
            print(f"一天总结: {day_summary['narrative'][:100]}...")
        
    else:
        print("✗ 行动处理失败")


def debug_file_system():
    """调试文件系统"""
    print("\n=== 调试文件系统 ===")
    
    from services.file_storage_service import get_storage_service
    storage_service = get_storage_service()
    
    # 检查目录结构
    print("1. 检查目录结构...")
    data_dir = "backend/data"
    games_dir = os.path.join(data_dir, "games")
    backups_dir = os.path.join(data_dir, "backups")
    logs_dir = os.path.join(data_dir, "logs")
    
    for directory in [data_dir, games_dir, backups_dir, logs_dir]:
        exists = os.path.exists(directory)
        print(f"   {directory}: {'存在' if exists else '不存在'}")
        if exists:
            files = os.listdir(directory)
            print(f"     文件数量: {len(files)}")
    
    # 获取存储统计
    print("2. 存储统计...")
    stats = storage_service.get_storage_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # 列出所有游戏
    print("3. 游戏列表...")
    games = storage_service.list_all_games(include_expired=True)
    print(f"   总游戏数: {len(games)}")
    for game in games[:3]:  # 只显示前3个
        print(f"   - {game.get('game_id', '未知')}: {game.get('player_name', '未知')}")


def debug_llm_integration():
    """调试LLM集成"""
    print("\n=== 调试LLM集成 ===")
    
    from llm.chat import create_chat_completion
    
    # 测试简单的LLM调用
    print("1. 测试LLM连接...")
    try:
        response = create_chat_completion(
            prompt="请回复'连接成功'",
            system_message="你是一个测试助手"
        )
        
        if response:
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"   LLM响应: {content}")
            print("   ✓ LLM连接正常")
        else:
            print("   ✗ LLM响应为空")
            
    except Exception as e:
        print(f"   ✗ LLM连接失败: {e}")


def run_full_debug():
    """运行完整的调试流程"""
    print("《五日勇者》调试工具")
    print("=" * 50)
    
    # 启用调试日志
    enable_debug_logging()
    
    # 调试文件系统
    debug_file_system()
    
    # 调试LLM集成
    debug_llm_integration()
    
    # 创建调试游戏
    game_id = create_debug_game()
    if not game_id:
        print("无法创建调试游戏，停止调试")
        return
    
    # 调试游戏状态
    debug_game_state(game_id)
    
    # 调试行动处理
    debug_action_processing(game_id)
    
    # 再次检查游戏状态
    print("\n=== 行动处理后的游戏状态 ===")
    debug_game_state(game_id)
    
    print("\n" + "=" * 50)
    print("调试完成！")
    print(f"调试游戏ID: {game_id}")


def interactive_debug():
    """交互式调试"""
    print("交互式调试模式")
    print("可用命令:")
    print("  1 - 创建调试游戏")
    print("  2 - 调试游戏状态")
    print("  3 - 调试行动处理")
    print("  4 - 调试文件系统")
    print("  5 - 调试LLM集成")
    print("  6 - 运行完整调试")
    print("  q - 退出")
    
    game_id = None
    
    while True:
        command = input("\n请输入命令: ").strip()
        
        if command == 'q':
            break
        elif command == '1':
            game_id = create_debug_game()
        elif command == '2':
            if game_id:
                debug_game_state(game_id)
            else:
                print("请先创建调试游戏")
        elif command == '3':
            if game_id:
                action = input("请输入行动描述: ").strip()
                if action:
                    debug_action_processing(game_id, action)
                else:
                    debug_action_processing(game_id)
            else:
                print("请先创建调试游戏")
        elif command == '4':
            debug_file_system()
        elif command == '5':
            debug_llm_integration()
        elif command == '6':
            run_full_debug()
        else:
            print("无效命令")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'interactive':
        interactive_debug()
    else:
        run_full_debug()
