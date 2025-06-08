#!/usr/bin/env python3
"""
测试超时修复效果的脚本
"""

import requests
import json
import time
from datetime import datetime

def test_game_action_with_timeout():
    """测试游戏行动处理的超时修复"""
    
    print("=" * 60)
    print("测试游戏行动处理超时修复")
    print("=" * 60)
    
    base_url = "http://localhost:5001/api"
    
    # 1. 创建游戏会话
    print("\n1. 创建游戏会话...")
    create_session_data = {
        "initial_data": {
            "day": 1,
            "player": {
                "name": "测试勇者",
                "stats": {"hp": 100, "mp": 100, "strength": 10, "intelligence": 10, "agility": 10, "luck": 10},
                "inventory": []
            },
            "world": {
                "weather": "晴天",
                "current_location": "村庄",
                "current_time": "上午"
            },
            "npc": {
                "village_chief": {
                    "name": "村长",
                    "profession": "村长",
                    "relationship": 0
                }
            }
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/game/session/create",
            json=create_session_data,
            timeout=30
        )
        response.raise_for_status()
        
        session_data = response.json()
        if session_data["status"] != "success":
            print(f"❌ 创建会话失败: {session_data.get('message', '未知错误')}")
            return False
            
        game_id = session_data["game_id"]
        print(f"✅ 游戏会话创建成功: {game_id}")
        
    except Exception as e:
        print(f"❌ 创建会话异常: {e}")
        return False
    
    # 2. 测试游戏行动处理
    print("\n2. 测试游戏行动处理...")
    action_data = {
        "game_id": game_id,
        "action": "我想去村庄中心广场看看，了解一下当前的情况，并与村民们交谈。"
    }
    
    print(f"📝 行动内容: {action_data['action']}")
    print(f"⏰ 开始时间: {datetime.now().strftime('%H:%M:%S')}")
    
    start_time = time.time()
    
    try:
        # 使用90秒超时时间测试
        response = requests.post(
            f"{base_url}/game/action",
            json=action_data,
            timeout=90
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"⏰ 结束时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"⏱️  总耗时: {processing_time:.2f}秒")
        
        response.raise_for_status()
        result = response.json()
        
        if result["status"] == "success":
            print("✅ 游戏行动处理成功!")
            print(f"📊 响应数据大小: {len(json.dumps(result))} 字符")
            
            # 显示结果摘要
            if "result" in result:
                action_result = result["result"]
                if "day_summary" in action_result:
                    summary = action_result["day_summary"]
                    print(f"📖 事件摘要: {summary.get('narrative', '无')[:100]}...")
                
                if "time_progression" in action_result:
                    time_prog = action_result["time_progression"]
                    print(f"🕐 时间推演包含时段: {list(time_prog.keys())}")
            
            return True
        else:
            print(f"❌ 游戏行动处理失败: {result.get('message', '未知错误')}")
            return False
            
    except requests.exceptions.Timeout:
        end_time = time.time()
        processing_time = end_time - start_time
        print(f"⏰ 超时时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"⏱️  超时前耗时: {processing_time:.2f}秒")
        print("❌ 请求超时 - 这表明LLM处理时间超过90秒")
        return False
        
    except requests.exceptions.RequestException as e:
        end_time = time.time()
        processing_time = end_time - start_time
        print(f"⏰ 异常时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"⏱️  异常前耗时: {processing_time:.2f}秒")
        print(f"❌ 请求异常: {e}")
        return False
    
    except Exception as e:
        end_time = time.time()
        processing_time = end_time - start_time
        print(f"⏰ 异常时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"⏱️  异常前耗时: {processing_time:.2f}秒")
        print(f"❌ 其他异常: {e}")
        return False

def test_health_check():
    """测试健康检查接口"""
    print("\n3. 测试健康检查...")
    
    try:
        response = requests.get("http://localhost:5001/api/game/health", timeout=5)
        response.raise_for_status()
        result = response.json()
        
        if result.get("status") == "ok":
            print("✅ 后端服务正常运行")
            return True
        else:
            print("❌ 后端服务状态异常")
            return False
            
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试超时修复效果...")
    
    # 测试健康检查
    if not test_health_check():
        print("\n❌ 后端服务不可用，请先启动后端服务")
        exit(1)
    
    # 测试游戏行动处理
    success = test_game_action_with_timeout()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 测试完成 - 超时修复生效!")
        print("✅ 游戏第一天行动处理成功")
        print("📝 建议:")
        print("   - 前端超时时间已增加到90秒")
        print("   - 后端LLM调用超时时间设置为60秒")
        print("   - 增加了详细的调试日志")
    else:
        print("❌ 测试失败 - 需要进一步调试")
        print("📝 建议:")
        print("   - 检查后端日志获取详细错误信息")
        print("   - 确认LLM服务可用性")
        print("   - 检查网络连接")
    
    print("=" * 60)
