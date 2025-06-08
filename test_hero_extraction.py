#!/usr/bin/env python3
"""
测试勇者信息提取功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from utils.text_analyzer import extract_hero_info

def test_hero_extraction():
    """测试不同类型的勇者描述"""
    
    test_cases = [
        {
            "description": "基本描述",
            "input": "我是一个勇者，名叫艾伦，是个男性，今年25岁。"
        },
        {
            "description": "有力量描述",
            "input": "我是一个非常强壮的勇者，力量很大，智力一般，身手敏捷，运气不错。"
        },
        {
            "description": "极强属性描述", 
            "input": "我是一个极其强壮的战士，拥有超凡的智慧，身手极其敏捷，运气极佳。"
        },
        {
            "description": "数值描述",
            "input": "我是一个勇者，力量80，智力70，敏捷60，幸运90。"
        },
        {
            "description": "无属性描述",
            "input": "我是一个普通的勇者，没有什么特别的能力。"
        },
        {
            "description": "负面描述",
            "input": "我是一个体弱的勇者，不太聪明，行动迟缓，运气很差。"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n=== 测试 {i}: {test_case['description']} ===")
        print(f"输入: {test_case['input']}")
        
        try:
            result = extract_hero_info(test_case['input'])
            print(f"提取结果:")
            print(f"  姓名: {result.get('name')}")
            print(f"  性别: {result.get('gender')}")
            print(f"  职业: {result.get('profession')}")
            print(f"  年龄: {result.get('age')}")
            print(f"  属性:")
            stats = result.get('stats', {})
            print(f"    力量: {stats.get('strength')}")
            print(f"    智力: {stats.get('intelligence')}")
            print(f"    敏捷: {stats.get('agility')}")
            print(f"    幸运: {stats.get('luck')}")
        except Exception as e:
            print(f"提取失败: {e}")

if __name__ == "__main__":
    test_hero_extraction()
