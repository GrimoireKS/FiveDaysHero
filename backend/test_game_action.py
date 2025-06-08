#!/usr/bin/env python3
"""
测试游戏行动处理功能
"""

import json
from services import get_game_data_service, get_game_action_service


def create_test_game():
    """创建测试游戏"""
    print("=== 创建测试游戏 ===")
    
    game_data_service = get_game_data_service()
    
    # 创建测试游戏数据
    initial_data = {
        "player": {
            "name": "测试勇者",
            "gender": "男",
            "profession": "战士",
            "age": 25,
            "stats": {
                "hp": 100,
                "mp": 100,
                "strength": 15,
                "intelligence": 10,
                "agility": 12,
                "luck": 8
            },
            "equipment": {
                "chest": "皮甲",
                "hands": ["铁剑"],
                "feet": "皮靴"
            }
        },
        "world": {
            "current_day": 1,
            "current_time": "上午",
            "weather": "晴天",
            "locations": {
                "village": {
                    "name": "新手村",
                    "description": "一个宁静的小村庄",
                    "type": "settlement",
                    "safety_level": "safe"
                },
                "forest": {
                    "name": "幽暗森林",
                    "description": "充满危险的森林",
                    "type": "wilderness",
                    "safety_level": "dangerous"
                }
            }
        },
        "npc": {
            "village_chief": {
                "name": "村长",
                "profession": "村长",
                "age": 60,
                "gender": "男",
                "relationship": 0,
                "stats": {
                    "strength": 5,
                    "intelligence": 15,
                    "agility": 3,
                    "luck": 10
                }
            },
            "blacksmith": {
                "name": "铁匠",
                "profession": "铁匠",
                "age": 45,
                "gender": "男",
                "relationship": 0,
                "stats": {
                    "strength": 18,
                    "intelligence": 12,
                    "agility": 8,
                    "luck": 7
                }
            }
        },
        "history": [],
        "events": []
    }
    
    game_id = game_data_service.create_new_game(initial_data)
    
    if game_id:
        print(f"✓ 测试游戏创建成功: {game_id}")
        return game_id
    else:
        print("✗ 测试游戏创建失败")
        return None


def test_player_action(game_id: str):
    """测试玩家行动处理"""
    print(f"\n=== 测试玩家行动处理 ===")
    
    game_action_service = get_game_action_service()
    
    # 测试行动1：探索村庄
    print("测试行动1：探索村庄")
    action1 = "我想在村庄里四处走走，了解一下这个地方的情况，和村民们聊聊天，看看有什么任务可以做。"
    
    result1 = game_action_service.process_player_action(game_id, action1)
    
    if result1:
        print("✓ 行动1处理成功")
        print(f"  - 玩家行动分解:")
        player_actions = result1.get('player_actions', {})
        for time_period, action in player_actions.items():
            print(f"    {time_period}: {action}")
        
        print(f"  - 一天总结: {result1.get('day_summary', {}).get('narrative', '无')}")
        
        # 显示状态变化
        updated_states = result1.get('updated_states', {})
        if 'player' in updated_states:
            player_stats = updated_states['player']
            print(f"  - 玩家状态: HP={player_stats.get('hp', 'N/A')}, MP={player_stats.get('mp', 'N/A')}")
        
    else:
        print("✗ 行动1处理失败")
        return False
    
    # 获取更新后的游戏状态
    game_data_service = get_game_data_service()
    updated_state = game_data_service.get_game_state(game_id)
    
    if updated_state:
        print(f"✓ 游戏状态更新成功，当前第{updated_state.get('day', 1)}天")
    else:
        print("✗ 获取更新后的游戏状态失败")
        return False
    
    return True


def test_multiple_actions(game_id: str):
    """测试多个连续行动"""
    print(f"\n=== 测试多个连续行动 ===")
    
    game_action_service = get_game_action_service()
    game_data_service = get_game_data_service()
    
    actions = [
        "我要去森林里探险，寻找一些有用的材料和宝物，同时锻炼自己的战斗技能。",
        "我想回到村庄，把今天的收获整理一下，然后去找铁匠看看能不能升级装备。",
        "我要继续深入森林，寻找更强大的怪物来挑战，提升自己的实力。"
    ]
    
    for i, action in enumerate(actions, 2):
        print(f"\n测试行动{i}：")
        print(f"行动描述：{action}")
        
        # 检查游戏是否已完成
        if game_data_service.is_game_completed(game_id):
            print("游戏已完成，停止测试")
            break
        
        result = game_action_service.process_player_action(game_id, action)
        
        if result:
            print(f"✓ 行动{i}处理成功")
            
            # 显示简要结果
            day_summary = result.get('day_summary', {})
            if day_summary.get('narrative'):
                print(f"  - 总结: {day_summary['narrative'][:100]}...")
            
            # 显示重要事件
            major_events = day_summary.get('major_events', [])
            if major_events:
                print(f"  - 重要事件: {', '.join(major_events[:2])}")
            
        else:
            print(f"✗ 行动{i}处理失败")
            break
        
        # 获取当前游戏状态
        current_state = game_data_service.get_game_state(game_id)
        if current_state:
            current_day = current_state.get('day', 1)
            player_hp = current_state.get('player', {}).get('stats', {}).get('hp', 100)
            print(f"  - 当前状态: 第{current_day}天, HP={player_hp}")
    
    return True


def test_game_completion(game_id: str):
    """测试游戏完成状态"""
    print(f"\n=== 测试游戏完成状态 ===")
    
    game_data_service = get_game_data_service()
    
    # 检查游戏是否完成
    is_completed = game_data_service.is_game_completed(game_id)
    print(f"游戏完成状态: {is_completed}")
    
    # 获取最终游戏状态
    final_state = game_data_service.get_game_state(game_id)
    if final_state:
        print(f"最终天数: 第{final_state.get('day', 1)}天")
        
        # 显示历史记录
        history = final_state.get('history', [])
        if history:
            print("游戏历史:")
            for event in history[-3:]:  # 显示最后3个事件
                print(f"  - {event}")
    
    return True


def main():
    """主测试函数"""
    print("开始测试游戏行动处理功能")
    print("=" * 50)
    
    try:
        # 创建测试游戏
        game_id = create_test_game()
        if not game_id:
            print("无法创建测试游戏，停止测试")
            return
        
        # 测试单个行动
        if not test_player_action(game_id):
            print("单个行动测试失败")
            return
        
        # 测试多个连续行动
        if not test_multiple_actions(game_id):
            print("多个行动测试失败")
            return
        
        # 测试游戏完成状态
        if not test_game_completion(game_id):
            print("游戏完成状态测试失败")
            return
        
        print("\n" + "=" * 50)
        print("✓ 所有测试通过！")
        print("游戏行动处理功能工作正常")
        print(f"测试游戏ID: {game_id}")
        
    except Exception as e:
        print(f"\n✗ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
