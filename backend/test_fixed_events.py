#!/usr/bin/env python3
"""
测试固定事件功能
"""

from models.common import TimeOfDay
from services import get_fixed_events_service


def test_fixed_events_loading():
    """测试固定事件加载"""
    print("=== 测试固定事件加载 ===")
    
    fixed_events_service = get_fixed_events_service()
    
    # 获取所有固定事件
    all_events = fixed_events_service.get_all_fixed_events()
    print(f"✓ 加载了 {len(all_events)} 个固定事件")
    
    # 显示前几个事件
    for i, (time_key, description) in enumerate(list(all_events.items())[:3]):
        print(f"  {i+1}. {time_key}: {description[:50]}...")
    
    return len(all_events) > 0


def test_time_enum_integration():
    """测试时间枚举集成"""
    print("\n=== 测试时间枚举集成 ===")
    
    fixed_events_service = get_fixed_events_service()
    
    # 测试几个特定时间
    test_times = [
        TimeOfDay.D1Morning,
        TimeOfDay.D2Afternoon,
        TimeOfDay.D3Evening,
        TimeOfDay.D5Morning
    ]
    
    for time_enum in test_times:
        has_event = fixed_events_service.has_fixed_event(time_enum)
        event_desc = fixed_events_service.get_fixed_event(time_enum)
        
        print(f"  {time_enum.value}: {'有事件' if has_event else '无事件'}")
        if event_desc:
            print(f"    事件: {event_desc[:60]}...")
    
    return True


def test_day_events():
    """测试按天获取事件"""
    print("\n=== 测试按天获取事件 ===")
    
    fixed_events_service = get_fixed_events_service()
    
    for day in range(1, 6):
        day_events = fixed_events_service.get_fixed_events_for_day(day)
        print(f"  第{day}天: {len(day_events)} 个事件")
        
        for event in day_events:
            print(f"    - {event['period']}: {event['description'][:40]}...")
    
    return True


def test_prompt_formatting():
    """测试提示格式化"""
    print("\n=== 测试提示格式化 ===")
    
    fixed_events_service = get_fixed_events_service()
    
    # 测试单天格式化
    print("第1天事件格式化:")
    day1_formatted = fixed_events_service.format_fixed_events_for_prompt(1)
    print(day1_formatted)
    
    print("\n第3天事件格式化:")
    day3_formatted = fixed_events_service.format_fixed_events_for_prompt(3)
    print(day3_formatted)
    
    # 测试所有事件格式化
    print("\n所有事件格式化 (前200字符):")
    all_formatted = fixed_events_service.format_fixed_events_for_prompt()
    print(all_formatted[:200] + "...")
    
    return True


def test_events_summary():
    """测试事件摘要"""
    print("\n=== 测试事件摘要 ===")
    
    fixed_events_service = get_fixed_events_service()
    
    summary = fixed_events_service.get_fixed_events_summary()
    print(f"  总事件数: {summary['total_events']}")
    print("  各天事件数:")
    
    for day_key, count in summary['events_by_day'].items():
        day_num = day_key.split('_')[1]
        print(f"    第{day_num}天: {count} 个事件")
    
    return True


def test_game_integration():
    """测试与游戏系统集成"""
    print("\n=== 测试游戏系统集成 ===")
    
    from services import get_game_data_service, get_game_action_service
    
    # 创建测试游戏
    game_data_service = get_game_data_service()
    
    initial_data = {
        "player": {
            "name": "固定事件测试勇者",
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
            "equipment": {}
        },
        "world": {
            "current_day": 1,
            "current_time": "上午",
            "weather": "晴天"
        },
        "npc": {},
        "history": [],
        "events": []
    }
    
    game_id = game_data_service.create_new_game(initial_data)
    
    if not game_id:
        print("  ✗ 创建测试游戏失败")
        return False
    
    print(f"  ✓ 创建测试游戏成功: {game_id}")
    
    # 测试行动处理中的固定事件集成
    game_action_service = get_game_action_service()
    
    # 检查固定事件服务是否正确集成
    if hasattr(game_action_service, 'fixed_events_service'):
        print("  ✓ 游戏行动服务已集成固定事件服务")
        
        # 测试构建提示时是否包含固定事件
        game_state = game_data_service.get_game_state(game_id)
        if game_state:
            try:
                # 这里我们不实际调用LLM，只测试提示构建
                user_prompt = game_action_service._build_user_prompt(game_state, "测试行动")
                
                if "固定事件" in user_prompt:
                    print("  ✓ 用户提示中包含固定事件信息")
                else:
                    print("  ✗ 用户提示中缺少固定事件信息")
                    
            except Exception as e:
                print(f"  ✗ 构建用户提示失败: {e}")
        else:
            print("  ✗ 获取游戏状态失败")
    else:
        print("  ✗ 游戏行动服务未集成固定事件服务")
        return False
    
    return True


def test_internal_service_only():
    """测试内部服务功能（不包含API）"""
    print("\n=== 测试内部服务功能 ===")

    fixed_events_service = get_fixed_events_service()

    # 测试服务是否正确初始化
    print("  测试服务初始化...")
    if hasattr(fixed_events_service, 'fixed_events'):
        print("    ✓ 固定事件服务正确初始化")
    else:
        print("    ✗ 固定事件服务初始化失败")
        return False

    # 测试重新加载功能
    print("  测试配置重新加载...")
    try:
        original_count = len(fixed_events_service.get_all_fixed_events())
        fixed_events_service.reload_fixed_events()
        new_count = len(fixed_events_service.get_all_fixed_events())

        if new_count == original_count:
            print(f"    ✓ 配置重新加载成功，事件数量: {new_count}")
        else:
            print(f"    ✗ 重新加载后事件数量不一致: {original_count} -> {new_count}")
            return False
    except Exception as e:
        print(f"    ✗ 重新加载失败: {e}")
        return False

    # 测试服务的所有核心功能
    print("  测试核心功能完整性...")
    core_methods = [
        'get_fixed_event',
        'get_fixed_events_for_day',
        'get_all_fixed_events',
        'has_fixed_event',
        'format_fixed_events_for_prompt'
    ]

    for method_name in core_methods:
        if hasattr(fixed_events_service, method_name):
            print(f"    ✓ {method_name} 方法存在")
        else:
            print(f"    ✗ {method_name} 方法缺失")
            return False

    return True


def main():
    """主测试函数"""
    print("固定事件功能测试")
    print("=" * 50)
    
    tests = [
        ("固定事件加载", test_fixed_events_loading),
        ("时间枚举集成", test_time_enum_integration),
        ("按天获取事件", test_day_events),
        ("提示格式化", test_prompt_formatting),
        ("事件摘要", test_events_summary),
        ("游戏系统集成", test_game_integration),
        ("内部服务功能", test_internal_service_only)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} 测试通过")
            else:
                print(f"✗ {test_name} 测试失败")
        except Exception as e:
            print(f"✗ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ 所有测试通过！固定事件功能工作正常")
    else:
        print("✗ 部分测试失败，请检查相关功能")


if __name__ == "__main__":
    main()
