"""
勇者相关API接口
"""

import random
from flask import Blueprint, request, jsonify
from utils.text_analyzer import extract_hero_info, extract_equipment
from models import Hero

# 创建蓝图
hero_bp = Blueprint('hero', __name__)


def _apply_profession_bonuses(base_stats, profession):
    """
    根据职业应用属性加成

    Args:
        base_stats (dict): 基础属性
        profession (str): 职业名称

    Returns:
        dict: 调整后的属性
    """
    adjusted_stats = base_stats.copy()

    # 职业关键词映射
    profession_bonuses = {
        # 战士类
        '战士': {'strength': 15, 'agility': 5},
        '骑士': {'strength': 15, 'agility': 5},
        '剑客': {'strength': 15, 'agility': 5},
        '武者': {'strength': 15, 'agility': 5},
        '剑士': {'strength': 15, 'agility': 5},

        # 法师类
        '法师': {'intelligence': 15},
        '魔法师': {'intelligence': 15},
        '术士': {'intelligence': 15},
        '巫师': {'intelligence': 15},
        '魔导师': {'intelligence': 15},

        # 盗贼类
        '盗贼': {'agility': 15, 'luck': 5},
        '刺客': {'agility': 15, 'luck': 5},
        '游侠': {'agility': 15, 'luck': 5},
        '忍者': {'agility': 15, 'luck': 5},
        '潜行者': {'agility': 15, 'luck': 5},

        # 诗人类
        '诗人': {'luck': 15, 'intelligence': 5},
        '音乐家': {'luck': 15, 'intelligence': 5},
        '吟游诗人': {'luck': 15, 'intelligence': 5},
        '艺术家': {'luck': 15, 'intelligence': 5},

        # 牧师类
        '牧师': {'intelligence': 10, 'luck': 10},
        '圣职者': {'intelligence': 10, 'luck': 10},
        '治疗师': {'intelligence': 10, 'luck': 10},
        '神官': {'intelligence': 10, 'luck': 10},

        # 商人类
        '商人': {'luck': 10, 'intelligence': 5},
        '贸易商': {'luck': 10, 'intelligence': 5},
        '商贾': {'luck': 10, 'intelligence': 5},
    }

    # 查找匹配的职业并应用加成
    for prof_key, bonuses in profession_bonuses.items():
        if prof_key in profession:
            for stat, bonus in bonuses.items():
                adjusted_stats[stat] = min(100, adjusted_stats[stat] + bonus)
            break

    return adjusted_stats


@hero_bp.route('/analyze', methods=['POST'])
def analyze_hero():
    """分析玩家输入，提取勇者信息"""
    data = request.json
    player_response = data.get('playerResponse', '')
    
    try:
        # 从玩家输入中提取勇者信息
        hero_info = extract_hero_info(player_response)
        equipment = extract_equipment(player_response)
        
        # 创建勇者对象
        hero = Hero(
            name=hero_info["name"] or "无名勇者",
            gender=hero_info["gender"] or "未知",
            profession=hero_info["profession"] or "勇者",
            age=hero_info["age"] or random.randint(18, 30)
        )
        
        # 更新勇者属性，未提取到的属性使用默认值50
        base_stats = {
            "strength": hero_info["stats"]["strength"] or 50,
            "intelligence": hero_info["stats"]["intelligence"] or 50,
            "agility": hero_info["stats"]["agility"] or 50,
            "luck": hero_info["stats"]["luck"] or 50
        }

        # 根据职业进行属性调整
        profession = hero_info.get("profession", "").lower()
        adjusted_stats = _apply_profession_bonuses(base_stats, profession)

        hero.stats.update(adjusted_stats)
        
        # 添加装备
        for slot, item in equipment.items():
            if item:  # 只添加非空装备
                hero.add_equipment(slot, item)
        
        return jsonify({
            "status": "success", 
            "hero": hero.to_dict(),
            "message": "勇者信息分析完成"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
