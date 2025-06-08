#!/usr/bin/env python3
"""
剧情推演API测试脚本
"""

import requests
import json


def test_story_progression_api():
    """测试剧情推演API"""
    print("开始测试剧情推演API...")
    
    # API端点
    url = "http://localhost:5001/api/story/progress"
    
    # 测试数据
    test_data = {
        "location": {
            "name": "村庄中心",
            "description": "一个宁静的小村庄中心，有一口古老的水井和几间茅草屋",
            "current_characters": ["勇者", "村长", "铁匠"],
            "special_properties": {
                "atmosphere": "peaceful",
                "time_of_day": "morning",
                "weather": "sunny"
            }
        },
        "character_actions": [
            {
                "character_name": "勇者",
                "action_description": "向村长询问关于魔王的传说",
                "location": "村庄中心"
            },
            {
                "character_name": "村长",
                "action_description": "正在和其他村民讨论最近的异象",
                "location": "村庄中心"
            },
            {
                "character_name": "铁匠",
                "action_description": "在水井边清洗刚打造的武器",
                "location": "村庄中心"
            }
        ],
        "world_history": [
            "第一天上午：勇者来到了村庄",
            "村民们对突然出现的勇者感到好奇",
            "国王的使者昨天宣布了魔王即将降临的消息"
        ],
        "current_time": "D1Morning",
        "current_world_state": {
            "weather": "晴天",
            "atmosphere": "紧张中带着希望",
            "day": 1,
            "time": "上午",
            "global_threat_level": "medium"
        },
        "current_character_states": {
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
    }
    
    try:
        # 发送POST请求
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=60
        )
        
        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            print("✅ API调用成功！")
            print(f"状态: {result.get('status')}")
            print(f"消息: {result.get('message')}")
            
            if 'result' in result:
                story_result = result['result']
                print("\n=== 推演结果 ===")
                print(f"事件总结: {story_result.get('event_summary')}")
                print(f"\n叙述描述: {story_result.get('narrative_description')}")
                
                print("\n=== 角色状态更新 ===")
                for char_name, state in story_result.get('updated_character_states', {}).items():
                    print(f"{char_name}: {state}")
                
                print("\n=== 世界状态更新 ===")
                print(json.dumps(story_result.get('updated_world_state'), ensure_ascii=False, indent=2))
                
                print("\n=== 关系变化 ===")
                print(json.dumps(story_result.get('relationship_changes'), ensure_ascii=False, indent=2))
            
            return True
        else:
            print(f"❌ API调用失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False


if __name__ == "__main__":
    success = test_story_progression_api()
    if success:
        print("\n🎉 API测试通过！")
    else:
        print("\n💥 API测试失败！")
