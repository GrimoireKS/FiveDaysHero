#!/usr/bin/env python3
"""
剧情推演引擎测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from models import CharacterAction, LocationInfo, TimeOfDay
from llm.story_engine import create_story_progression


def test_story_progression():
    """测试剧情推演功能"""
    print("开始测试剧情推演功能...")
    
    # 创建测试数据
    location = LocationInfo(
        name="村庄中心",
        description="一个宁静的小村庄中心，有一口古老的水井和几间茅草屋",
        current_characters=["勇者", "村长", "铁匠"],
        special_properties={
            "atmosphere": "peaceful",
            "time_of_day": "morning",
            "weather": "sunny"
        }
    )
    
    character_actions = [
        CharacterAction(
            character_name="勇者",
            action_description="向村长询问关于魔王的传说",
            location="村庄中心"
        ),
        CharacterAction(
            character_name="村长",
            action_description="正在和其他村民讨论最近的异象",
            location="村庄中心"
        ),
        CharacterAction(
            character_name="铁匠",
            action_description="在水井边清洗刚打造的武器",
            location="村庄中心"
        )
    ]
    
    world_history = [
        "第一天上午：勇者来到了村庄",
        "村民们对突然出现的勇者感到好奇",
        "国王的使者昨天宣布了魔王即将降临的消息"
    ]
    
    current_world_state = {
        "weather": "晴天",
        "atmosphere": "紧张中带着希望",
        "day": 1,
        "time": "上午",
        "global_threat_level": "medium"
    }
    
    current_character_states = {
        "勇者": {
            "stats": {
                "hp": 100,
                "mp": 100,
                "strength": 15,
                "intelligence": 12,
                "agility": 10,
                "luck": 8
            },
            "relationship": 0,
            "equipment": {"weapon": "铁剑", "armor": "皮甲"},
            "inventory": ["生命药水", "面包"],
            "status_effects": []
        },
        "村长": {
            "stats": {
                "hp": 80,
                "mp": 50,
                "strength": 8,
                "intelligence": 18,
                "agility": 6,
                "luck": 12
            },
            "relationship": 5,
            "equipment": {},
            "inventory": ["村庄钥匙", "古老地图"],
            "status_effects": []
        },
        "铁匠": {
            "stats": {
                "hp": 120,
                "mp": 30,
                "strength": 20,
                "intelligence": 10,
                "agility": 8,
                "luck": 7
            },
            "relationship": 0,
            "equipment": {"tool": "铁锤"},
            "inventory": ["铁矿石", "煤炭"],
            "status_effects": []
        }
    }
    
    try:
        # 执行剧情推演
        result = create_story_progression(
            location=location,
            character_actions=character_actions,
            world_history=world_history,
            current_time=TimeOfDay.D1Morning,
            current_world_state=current_world_state,
            current_character_states=current_character_states
        )
        
        print("剧情推演成功！")
        print("\n=== 推演结果 ===")
        print(f"事件总结: {result.event_summary}")
        print(f"\n叙述描述: {result.narrative_description}")
        
        print("\n=== 角色状态更新 ===")
        for char_name, state in result.updated_character_states.items():
            print(f"{char_name}: {state}")
        
        print("\n=== 世界状态更新 ===")
        print(result.updated_world_state)
        
        print("\n=== 关系变化 ===")
        print(result.relationship_changes)
        
        return True
        
    except Exception as e:
        print(f"剧情推演失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_story_progression()
    if success:
        print("\n✅ 测试通过！")
    else:
        print("\n❌ 测试失败！")
        sys.exit(1)
