#!/usr/bin/env python3
"""
游戏流程示例
演示如何使用新的游戏行动处理API
"""

import requests
import json
import time


def create_game_session():
    """创建游戏会话"""
    print("=== 创建游戏会话 ===")
    
    url = "http://localhost:5001/api/world/create"
    data = {
        "playerResponse": "我是一个年轻的战士，名叫艾伦，手持一把铁剑，身穿简单的皮甲。我勇敢而正义，希望能够帮助村民们解决困难，成为一名真正的英雄。"
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get("status") == "success":
            game_id = result.get("game_id")
            print(f"✓ 游戏会话创建成功")
            print(f"  游戏ID: {game_id}")
            print(f"  勇者姓名: {result.get('hero', {}).get('name', '未知')}")
            return game_id
        else:
            print(f"✗ 游戏会话创建失败: {result.get('message', '未知错误')}")
            return None
            
    except Exception as e:
        print(f"✗ 创建游戏会话时发生异常: {e}")
        return None


def process_action(game_id, action_description):
    """处理玩家行动"""
    print(f"\n--- 处理玩家行动 ---")
    print(f"行动描述: {action_description}")
    
    url = "http://localhost:5001/api/game/action"
    data = {
        "game_id": game_id,
        "action": action_description
    }
    
    try:
        print("正在处理行动，请稍候...")
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get("status") == "success":
            print("✓ 行动处理成功")
            
            action_result = result.get("result", {})
            
            # 显示玩家行动分解
            player_actions = action_result.get("player_actions", {})
            print("\n玩家行动分解:")
            for time_period, action in player_actions.items():
                print(f"  {time_period}: {action}")
            
            # 显示时段进展
            time_progression = action_result.get("time_progression", {})
            print("\n时段进展:")
            for time_period, progress in time_progression.items():
                narrative = progress.get("narrative", "")
                events = progress.get("events", [])
                print(f"  {time_period}:")
                print(f"    叙述: {narrative[:100]}...")
                if events:
                    print(f"    事件: {', '.join(events[:2])}")
            
            # 显示一天总结
            day_summary = action_result.get("day_summary", {})
            if day_summary.get("narrative"):
                print(f"\n一天总结: {day_summary['narrative']}")
            
            # 显示重要事件
            major_events = day_summary.get("major_events", [])
            if major_events:
                print(f"重要事件: {', '.join(major_events)}")
            
            # 显示当前状态
            updated_game_state = result.get("updated_game_state", {})
            current_day = updated_game_state.get("day", 1)
            player_stats = updated_game_state.get("player", {}).get("stats", {})
            hp = player_stats.get("hp", 100)
            mp = player_stats.get("mp", 100)
            
            print(f"\n当前状态: 第{current_day}天, HP={hp}, MP={mp}")
            
            return True
            
        else:
            print(f"✗ 行动处理失败: {result.get('message', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"✗ 处理行动时发生异常: {e}")
        return False


def get_game_state(game_id):
    """获取游戏状态"""
    url = f"http://localhost:5001/api/game/session/{game_id}/state"
    
    try:
        response = requests.get(url)
        result = response.json()
        
        if result.get("status") == "success":
            return result.get("game_state")
        else:
            print(f"获取游戏状态失败: {result.get('message', '未知错误')}")
            return None
            
    except Exception as e:
        print(f"获取游戏状态时发生异常: {e}")
        return None


def main():
    """主函数 - 演示完整的游戏流程"""
    print("《五日勇者》游戏流程演示")
    print("=" * 50)
    
    # 1. 创建游戏会话
    game_id = create_game_session()
    if not game_id:
        print("无法创建游戏会话，演示结束")
        return
    
    # 2. 定义一系列游戏行动
    actions = [
        "我想在村庄里四处走走，了解一下这个地方的情况，和村民们聊聊天，看看有什么任务可以做。",
        "我要去森林里探险，寻找一些有用的材料和宝物，同时锻炼自己的战斗技能。",
        "我想回到村庄，把今天的收获整理一下，然后去找铁匠看看能不能升级装备。",
        "我要继续深入森林，寻找更强大的怪物来挑战，提升自己的实力。",
        "我要完成最后的准备，然后挑战森林深处的强大敌人，完成我的冒险之旅。"
    ]
    
    # 3. 逐个处理行动
    for i, action in enumerate(actions, 1):
        print(f"\n{'='*20} 第{i}天行动 {'='*20}")
        
        # 检查游戏状态
        current_state = get_game_state(game_id)
        if current_state:
            current_day = current_state.get("day", 1)
            if current_day > 5:
                print("游戏已完成！")
                break
        
        # 处理行动
        success = process_action(game_id, action)
        if not success:
            print("行动处理失败，演示结束")
            break
        
        # 等待一下，避免请求过于频繁
        time.sleep(2)
    
    # 4. 显示最终状态
    print(f"\n{'='*20} 游戏结束 {'='*20}")
    final_state = get_game_state(game_id)
    if final_state:
        final_day = final_state.get("day", 1)
        player = final_state.get("player", {})
        player_name = player.get("name", "未知勇者")
        
        print(f"勇者 {player_name} 的冒险在第{final_day}天结束")
        
        # 显示最终属性
        stats = player.get("stats", {})
        print(f"最终属性: HP={stats.get('hp', 100)}, MP={stats.get('mp', 100)}")
        print(f"力量={stats.get('strength', 0)}, 智力={stats.get('intelligence', 0)}")
        
        # 显示历史记录
        history = final_state.get("history", [])
        if history:
            print("\n冒险历程:")
            for event in history[-3:]:  # 显示最后3个事件
                print(f"  - {event}")
    
    print(f"\n演示完成！游戏ID: {game_id}")
    print("你可以使用这个ID继续游戏或查看详细信息")


if __name__ == "__main__":
    main()
