#!/usr/bin/env python3
"""
测试会话管理和文件存储系统
"""

import json
import time
from datetime import datetime

from services import get_game_data_service, get_session_service, get_storage_service
from utils.cleanup_tasks import get_cleanup_manager


def test_basic_functionality():
    """测试基本功能"""
    print("=== 测试基本功能 ===")
    
    # 获取服务实例
    game_data_service = get_game_data_service()
    session_service = get_session_service()
    storage_service = get_storage_service()
    
    print("✓ 服务实例创建成功")
    
    # 测试创建游戏
    initial_data = {
        "player": {
            "name": "测试勇者",
            "stats": {"strength": 10, "intelligence": 8, "agility": 12, "luck": 6},
            "equipment": {}
        },
        "world": {
            "current_day": 1,
            "current_time": "上午",
            "weather": "晴天"
        },
        "npc": {}
    }
    
    game_id = game_data_service.create_new_game(initial_data)
    if game_id:
        print(f"✓ 游戏创建成功: {game_id}")
    else:
        print("✗ 游戏创建失败")
        return False
    
    # 测试会话验证
    is_valid = session_service.validate_session(game_id)
    if is_valid:
        print("✓ 会话验证成功")
    else:
        print("✗ 会话验证失败")
        return False
    
    # 测试获取游戏状态
    game_state = game_data_service.get_game_state(game_id)
    if game_state:
        print("✓ 游戏状态获取成功")
        print(f"  - 玩家姓名: {game_state['player']['name']}")
        print(f"  - 当前天数: {game_state['day']}")
    else:
        print("✗ 游戏状态获取失败")
        return False
    
    # 测试更新游戏状态
    state_updates = {
        "day": 2,
        "player": {
            "stats": {"hp": 95}
        }
    }
    
    success = game_data_service.update_game_state(game_id, state_updates)
    if success:
        print("✓ 游戏状态更新成功")
        
        # 验证更新
        updated_state = game_data_service.get_game_state(game_id)
        if updated_state and updated_state['day'] == 2:
            print("✓ 状态更新验证成功")
        else:
            print("✗ 状态更新验证失败")
            return False
    else:
        print("✗ 游戏状态更新失败")
        return False
    
    # 测试会话信息
    session_info = session_service.get_session_info(game_id)
    if session_info:
        print("✓ 会话信息获取成功")
        print(f"  - 剩余时间: {session_info.get('remaining_time', '未知')}")
    else:
        print("✗ 会话信息获取失败")
        return False
    
    return game_id


def test_file_operations():
    """测试文件操作"""
    print("\n=== 测试文件操作 ===")
    
    storage_service = get_storage_service()
    
    # 获取存储统计
    stats = storage_service.get_storage_stats()
    print("✓ 存储统计获取成功")
    print(f"  - 总游戏数: {stats['total_games']}")
    print(f"  - 活跃游戏数: {stats['active_games']}")
    print(f"  - 存储大小: {stats['storage_size_mb']} MB")
    
    # 列出所有游戏
    games = storage_service.list_all_games()
    print(f"✓ 游戏列表获取成功，共 {len(games)} 个游戏")
    
    return True


def test_cleanup_functionality():
    """测试清理功能"""
    print("\n=== 测试清理功能 ===")
    
    cleanup_manager = get_cleanup_manager()
    
    # 获取下次清理时间
    next_times = cleanup_manager.get_next_cleanup_times()
    print("✓ 清理任务时间获取成功")
    for task, time_str in next_times.items():
        print(f"  - {task}: {time_str}")
    
    # 手动运行清理（只清理过期游戏）
    print("执行手动清理...")
    results = cleanup_manager.run_manual_cleanup("games")
    print(f"✓ 手动清理完成: {results}")
    
    return True


def test_session_lifecycle():
    """测试会话生命周期"""
    print("\n=== 测试会话生命周期 ===")
    
    session_service = get_session_service()
    
    # 列出所有会话
    sessions = session_service.list_user_sessions()
    print(f"✓ 当前活跃会话数: {len(sessions)}")
    
    if sessions:
        # 测试第一个会话的详细信息
        first_session = sessions[0]
        game_id = first_session['game_id']
        
        print(f"测试会话: {game_id}")
        
        # 获取剩余时间
        remaining_time = session_service.get_session_remaining_time(game_id)
        print(f"  - 剩余时间: {remaining_time}")
        
        # 测试延长有效期
        success = session_service.extend_session_expiry(game_id, 1)
        if success:
            print("✓ 会话有效期延长成功")
        else:
            print("✗ 会话有效期延长失败")
    
    # 获取会话统计
    stats = session_service.get_session_statistics()
    print("✓ 会话统计获取成功")
    print(f"  - 总会话数: {stats['total_sessions']}")
    print(f"  - 活跃会话数: {stats['active_sessions']}")
    
    return True


def main():
    """主测试函数"""
    print("开始测试会话管理和文件存储系统")
    print("=" * 50)
    
    try:
        # 测试基本功能
        game_id = test_basic_functionality()
        if not game_id:
            print("基本功能测试失败，停止测试")
            return
        
        # 测试文件操作
        if not test_file_operations():
            print("文件操作测试失败")
            return
        
        # 测试清理功能
        if not test_cleanup_functionality():
            print("清理功能测试失败")
            return
        
        # 测试会话生命周期
        if not test_session_lifecycle():
            print("会话生命周期测试失败")
            return
        
        print("\n" + "=" * 50)
        print("✓ 所有测试通过！")
        print("会话管理和文件存储系统工作正常")
        
    except Exception as e:
        print(f"\n✗ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
