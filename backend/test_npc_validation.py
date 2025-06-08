#!/usr/bin/env python3
"""
测试NPC验证功能
验证LLM只能操作预定义的NPC，不能创建新的NPC
"""

import json
from services import get_game_data_service, get_game_action_service


def create_test_game_with_predefined_npcs():
    """创建包含预定义NPC的测试游戏"""
    print("=== 创建包含预定义NPC的测试游戏 ===")
    
    game_data_service = get_game_data_service()
    
    # 创建测试游戏数据，使用预定义的NPC
    initial_data = {
        "day": 1,
        "player": {
            "basic_info": {
                "name": "测试勇者",
                "gender": "男",
                "profession": "战士",
                "age": 25
            },
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
                "castle": {
                    "name": "王城",
                    "description": "王国的首都",
                    "type": "settlement",
                    "safety_level": "safe"
                }
            }
        },
        "npc": {
            # 使用预定义的NPC
            "king": {
                "name": "国王",
                "profession": "国王",
                "age": 60,
                "gender": "男",
                "relationship": 0,
                "stats": {
                    "strength": 40,
                    "intelligence": 75,
                    "agility": 30,
                    "luck": 50
                },
                "description": "王国的统治者，智慧且公正，但最近因为王国的危机而忧心忡忡。"
            },
            "princess": {
                "name": "公主",
                "profession": "公主",
                "age": 20,
                "gender": "女",
                "relationship": 0,
                "stats": {
                    "strength": 60,
                    "intelligence": 80,
                    "agility": 60,
                    "luck": 65
                },
                "description": "王国的公主，聪明且勇敢，对冒险充满向往。具备一定武艺"
            },
            "innkeeper": {
                "name": "旅店老板",
                "profession": "旅店老板",
                "age": 50,
                "gender": "男",
                "relationship": 0,
                "stats": {
                    "strength": 40,
                    "intelligence": 55,
                    "agility": 35,
                    "luck": 60
                },
                "description": "村庄旅店的老板，热情好客，了解村庄的各种消息。"
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


def test_npc_validation_methods():
    """测试NPC验证相关方法"""
    print("\n=== 测试NPC验证方法 ===")
    
    game_action_service = get_game_action_service()
    
    # 测试获取预定义NPC列表
    print("测试获取预定义NPC列表...")
    predefined_npcs = game_action_service._get_predefined_npc_ids()
    print(f"预定义NPC数量: {len(predefined_npcs)}")
    print(f"预定义NPC列表: {sorted(list(predefined_npcs))[:10]}...")  # 显示前10个
    
    # 测试通过名称查找NPC ID
    print("\n测试通过名称查找NPC ID...")
    test_names = ["国王", "公主", "不存在的NPC"]
    for name in test_names:
        npc_id = game_action_service._find_npc_id_by_name(name)
        print(f"  {name} -> {npc_id}")
    
    # 测试NPC数据验证
    print("\n测试NPC数据验证...")
    test_npc_updates = {
        "king": {"relationship": 10},  # 有效的NPC
        "princess": {"relationship": 5},  # 有效的NPC
        "fake_npc": {"relationship": 20},  # 无效的NPC
        "another_fake": {"relationship": -10}  # 无效的NPC
    }
    
    print(f"验证前的NPC更新: {test_npc_updates}")
    game_action_service._validate_npc_data(test_npc_updates)
    print(f"验证后的NPC更新: {test_npc_updates}")
    
    return True


def test_npc_format_info(game_id: str):
    """测试NPC信息格式化"""
    print("\n=== 测试NPC信息格式化 ===")
    
    game_data_service = get_game_data_service()
    game_action_service = get_game_action_service()
    
    # 获取游戏状态
    game_state = game_data_service.get_game_state(game_id)
    if not game_state:
        print("✗ 无法获取游戏状态")
        return False
    
    # 测试NPC信息格式化
    npcs = game_state.get('npc', {})
    formatted_info = game_action_service._format_npc_info(npcs)
    
    print("格式化的NPC信息:")
    print(formatted_info)
    
    # 检查是否包含必要的信息
    required_elements = [
        "可操作的NPC列表",
        "只能修改这些NPC的状态",
        "不允许新增NPC",
        "重要提醒"
    ]
    
    for element in required_elements:
        if element in formatted_info:
            print(f"✓ 包含必要元素: {element}")
        else:
            print(f"✗ 缺少必要元素: {element}")
    
    return True


def test_action_with_invalid_npcs(game_id: str):
    """测试包含无效NPC的行动处理"""
    print("\n=== 测试包含无效NPC的行动处理 ===")
    
    game_action_service = get_game_action_service()
    
    # 创建一个可能导致LLM返回无效NPC的行动
    action = """我要去王城拜见国王，然后和公主聊天，同时我还想认识一些新的朋友，
    比如神秘的魔法师、强大的骑士、智慧的长老等等。我希望能够建立良好的关系。"""
    
    print(f"测试行动: {action}")
    
    # 处理行动
    result = game_action_service.process_player_action(game_id, action)
    
    if result:
        print("✓ 行动处理成功")
        
        # 检查返回的NPC更新
        updated_states = result.get('updated_states', {})
        npcs_updates = updated_states.get('npcs', {})
        
        print(f"返回的NPC更新: {list(npcs_updates.keys())}")
        
        # 验证所有返回的NPC都是预定义的
        predefined_npcs = game_action_service._get_predefined_npc_ids()
        invalid_npcs = []
        
        for npc_id in npcs_updates.keys():
            if npc_id not in predefined_npcs:
                invalid_npcs.append(npc_id)
        
        if invalid_npcs:
            print(f"✗ 发现无效的NPC: {invalid_npcs}")
            return False
        else:
            print("✓ 所有返回的NPC都是预定义的")
        
        # 检查游戏状态是否正确更新
        game_data_service = get_game_data_service()
        updated_game_state = game_data_service.get_game_state(game_id)
        
        if updated_game_state:
            final_npcs = updated_game_state.get('npc', {})
            print(f"最终游戏状态中的NPC: {list(final_npcs.keys())}")
            
            # 验证没有新增无效的NPC
            for npc_id in final_npcs.keys():
                if npc_id not in predefined_npcs:
                    print(f"✗ 游戏状态中发现无效NPC: {npc_id}")
                    return False
            
            print("✓ 游戏状态中没有无效的NPC")
        
    else:
        print("✗ 行动处理失败")
        return False
    
    return True


def main():
    """主测试函数"""
    print("开始测试NPC验证功能")
    print("=" * 50)
    
    try:
        # 测试NPC验证方法
        if not test_npc_validation_methods():
            print("NPC验证方法测试失败")
            return
        
        # 创建测试游戏
        game_id = create_test_game_with_predefined_npcs()
        if not game_id:
            print("无法创建测试游戏，停止测试")
            return
        
        # 测试NPC信息格式化
        if not test_npc_format_info(game_id):
            print("NPC信息格式化测试失败")
            return
        
        # 测试包含无效NPC的行动处理
        if not test_action_with_invalid_npcs(game_id):
            print("无效NPC行动处理测试失败")
            return
        
        print("\n" + "=" * 50)
        print("✓ 所有NPC验证测试通过！")
        print("NPC验证功能工作正常")
        print(f"测试游戏ID: {game_id}")
        
    except Exception as e:
        print(f"\n✗ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
