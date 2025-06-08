#!/usr/bin/env python3
"""
测试时间推演格式是否满足前端背景切换需求
"""

import json
from services import get_game_data_service, get_game_action_service


def create_test_game():
    """创建测试游戏"""
    print("=== 创建测试游戏 ===")
    
    game_data_service = get_game_data_service()
    
    initial_data = {
        "player": {
            "name": "时间推演测试勇者",
            "gender": "男",
            "profession": "战士",
            "age": 20,
            "stats": {
                "hp": 100,
                "mp": 100,
                "strength": 12,
                "intelligence": 8,
                "agility": 10,
                "luck": 7
            },
            "equipment": {
                "hands": ["铁剑"],
                "chest": "皮甲"
            }
        },
        "world": {
            "current_day": 1,
            "current_time": "上午",
            "weather": "晴天",
            "locations": {
                "village": {
                    "name": "新手村",
                    "description": "一个宁静的小村庄"
                },
                "forest": {
                    "name": "幽暗森林", 
                    "description": "充满危险的森林"
                }
            }
        },
        "npc": {
            "village_chief": {
                "name": "村长",
                "profession": "村长",
                "relationship": 0
            },
            "blacksmith": {
                "name": "铁匠",
                "profession": "铁匠",
                "relationship": 0
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


def test_time_progression_format(game_id: str):
    """测试时间推演格式"""
    print(f"\n=== 测试时间推演格式 ===")
    
    game_action_service = get_game_action_service()
    
    # 测试行动：涉及多个地点和不同类型的事件
    test_action = "我想先在村庄里和村民们交流，了解最近的情况，然后去森林边缘探索一下，看看有什么发现，晚上回到村庄休息。"
    
    print(f"测试行动: {test_action}")
    print("开始处理...")
    
    # 处理行动
    result = game_action_service.process_player_action(game_id, test_action)
    
    if not result:
        print("✗ 行动处理失败")
        return False
    
    print("✓ 行动处理成功")
    
    # 检查时间推演格式
    time_progression = result.get('time_progression', {})
    
    if not time_progression:
        print("✗ 缺少时间推演信息")
        return False
    
    print("\n=== 检查时间推演格式 ===")
    
    required_periods = ['morning', 'afternoon', 'evening']
    all_valid = True
    
    for period in required_periods:
        print(f"\n--- {period.upper()} ---")
        
        if period not in time_progression:
            print(f"✗ 缺少 {period} 时段")
            all_valid = False
            continue
        
        period_data = time_progression[period]
        
        # 检查必需字段
        required_fields = ['narrative', 'location', 'weather', 'atmosphere', 'events', 'state_changes']
        
        for field in required_fields:
            if field in period_data:
                print(f"✓ {field}: 存在")
                
                # 显示具体内容
                if field == 'narrative':
                    narrative = period_data[field]
                    print(f"  内容: {narrative[:60]}...")
                elif field == 'location':
                    location = period_data[field]
                    print(f"  地点: {location}")
                elif field == 'weather':
                    weather = period_data[field]
                    print(f"  天气: {weather}")
                elif field == 'atmosphere':
                    atmosphere = period_data[field]
                    print(f"  氛围: {atmosphere}")
                elif field == 'events':
                    events = period_data[field]
                    print(f"  事件数量: {len(events)}")
                    
                    # 检查事件格式
                    for i, event in enumerate(events):
                        if isinstance(event, dict):
                            event_type = event.get('type', '未知')
                            event_desc = event.get('description', '无描述')
                            event_location = event.get('location', '未知地点')
                            print(f"    事件{i+1}: {event_type} - {event_desc[:30]}... (地点: {event_location})")
                        else:
                            print(f"    事件{i+1}: {event} (旧格式)")
                            
            else:
                print(f"✗ {field}: 缺失")
                all_valid = False
    
    return all_valid


def analyze_background_switching_data(game_id: str):
    """分析背景切换所需的数据"""
    print(f"\n=== 分析背景切换数据 ===")
    
    game_action_service = get_game_action_service()
    
    # 测试不同类型的行动
    test_actions = [
        "我要在村庄里休息和购买装备",
        "我要去森林深处探险寻宝",
        "我要挑战森林中的强大怪物"
    ]
    
    for i, action in enumerate(test_actions, 1):
        print(f"\n--- 测试行动 {i} ---")
        print(f"行动: {action}")
        
        result = game_action_service.process_player_action(game_id, action)
        
        if not result:
            print("✗ 处理失败")
            continue
        
        time_progression = result.get('time_progression', {})
        
        # 分析每个时段的背景信息
        for period in ['morning', 'afternoon', 'evening']:
            if period in time_progression:
                period_data = time_progression[period]
                
                location = period_data.get('location', '未知')
                weather = period_data.get('weather', '未知')
                atmosphere = period_data.get('atmosphere', '未知')
                events = period_data.get('events', [])
                
                print(f"  {period}: {location} | {weather} | {atmosphere} | {len(events)}个事件")
                
                # 分析事件类型分布
                event_types = []
                for event in events:
                    if isinstance(event, dict):
                        event_types.append(event.get('type', '未知'))
                
                if event_types:
                    print(f"    事件类型: {', '.join(event_types)}")


def generate_frontend_format_example(game_id: str):
    """生成前端格式示例"""
    print(f"\n=== 生成前端格式示例 ===")
    
    game_action_service = get_game_action_service()
    
    action = "我要探索村庄周围的神秘遗迹"
    result = game_action_service.process_player_action(game_id, action)
    
    if not result:
        print("✗ 无法生成示例")
        return
    
    time_progression = result.get('time_progression', {})
    
    # 转换为前端友好的格式
    frontend_format = {
        "time_periods": []
    }
    
    for period in ['morning', 'afternoon', 'evening']:
        if period in time_progression:
            period_data = time_progression[period]
            
            frontend_period = {
                "period": period,
                "period_name": {"morning": "上午", "afternoon": "下午", "evening": "晚上"}[period],
                "background_info": {
                    "location": period_data.get('location', ''),
                    "weather": period_data.get('weather', ''),
                    "atmosphere": period_data.get('atmosphere', '')
                },
                "narrative": period_data.get('narrative', ''),
                "events": []
            }
            
            # 处理事件
            events = period_data.get('events', [])
            for event in events:
                if isinstance(event, dict):
                    frontend_event = {
                        "type": event.get('type', ''),
                        "description": event.get('description', ''),
                        "location": event.get('location', '')
                    }
                    frontend_period["events"].append(frontend_event)
            
            frontend_format["time_periods"].append(frontend_period)
    
    # 输出示例
    print("前端格式示例:")
    print(json.dumps(frontend_format, ensure_ascii=False, indent=2))


def main():
    """主测试函数"""
    print("时间推演格式测试")
    print("=" * 50)
    
    # 创建测试游戏
    game_id = create_test_game()
    if not game_id:
        print("无法创建测试游戏，停止测试")
        return
    
    # 测试时间推演格式
    format_valid = test_time_progression_format(game_id)
    
    if format_valid:
        print("\n✓ 时间推演格式验证通过")
        
        # 分析背景切换数据
        analyze_background_switching_data(game_id)
        
        # 生成前端格式示例
        generate_frontend_format_example(game_id)
        
        print("\n" + "=" * 50)
        print("✓ 测试完成！时间推演格式满足前端背景切换需求")
        print("\n前端可以使用的信息:")
        print("- location: 主要地点（用于选择背景图片）")
        print("- weather: 天气状况（用于天气效果）")
        print("- atmosphere: 氛围描述（用于滤镜或特效）")
        print("- events[].type: 事件类型（用于特殊背景或动画）")
        print("- events[].location: 具体地点（用于精确背景选择）")
        
    else:
        print("\n✗ 时间推演格式验证失败")
        print("需要检查LLM输出格式是否正确")


if __name__ == "__main__":
    main()
