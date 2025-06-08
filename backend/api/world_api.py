"""
世界相关API接口
"""

import random
import json
import os
from flask import Blueprint, request, jsonify
from utils.text_analyzer import extract_hero_info, extract_equipment
from models import World, Hero
from services import get_game_data_service


# 创建蓝图
world_bp = Blueprint('world', __name__)


def load_world_description():
    """从world_description.json文件加载世界基本描述"""
    world_desc_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'resources', 'world', 'world_description.json'
    )

    try:
        with open(world_desc_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"加载世界描述文件失败: {e}")
        # 返回默认的世界描述
        return {
            "world_name": "默认世界",
            "description": "一个基础的奇幻世界",
            "initial_locations": [
                {
                    "id": "village",
                    "name": "村庄",
                    "description": "一个平静的小村庄",
                    "type": "settlement",
                    "safety_level": "safe"
                }
            ],
            "world_rules": {
                "weather_system": {
                    "types": ["晴天", "雨天"]
                },
                "day_cycle": {
                    "times_of_day": ["上午", "下午", "晚上"]
                }
            }
        }


def generate_world_info(hero_data):
    """根据勇者信息生成世界基本情况"""
    # 加载世界基本描述
    world_desc = load_world_description()

    # 创建世界对象
    world = World(
        current_day=1,
        current_time=random.choice(world_desc["world_rules"]["day_cycle"]["times_of_day"]),
        weather=random.choice(world_desc["world_rules"]["weather_system"]["types"])
    )

    # 将世界描述信息存储在world对象中，以便在to_dict时使用
    world.world_info = {
        "name": world_desc["world_name"],
        "description": world_desc["description"],
        "background": world_desc.get("background", {}),
        "geography": world_desc.get("geography", {}),
        "lore": world_desc.get("lore", {}),
        "factions": world_desc.get("factions", [])
    }

    # 添加初始地点
    for location_data in world_desc["initial_locations"]:
        world.add_location(location_data["id"], {
            "name": location_data["name"],
            "description": location_data["description"],
            "type": location_data["type"],
            "safety_level": location_data["safety_level"],
            "available_services": location_data.get("available_services", []),
            "notable_npcs": location_data.get("notable_npcs", [])
        })

    return world


def generate_npc_info():
    """生成NPC信息"""
    import json
    import os
    from models import NPC
    
    # 读取NPC模板文件
    npc_template_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        'resources', 'npc', 'npc_templates.json'
    )
    
    npcs = {}
    
    try:
        with open(npc_template_path, 'r', encoding='utf-8') as file:
            npc_templates = json.load(file)
            
        # 根据模板创建NPC对象
        for npc_id, npc_data in npc_templates.items():
            npc = NPC(
                name=npc_data['name'],
                age=npc_data['age'],
                gender=npc_data['gender'],
                profession=npc_data['profession']
            )
            
            # 设置NPC属性
            for stat_name, stat_value in npc_data['stats'].items():
                npc.update_stats(stat_name, stat_value)

            # 设置与勇者的关系值（默认为0，后续通过RelationshipGraph管理）
            npc.update_relationship(0)

            # 初始化事件列表（事件在游戏过程中动态添加）
            npc.events = []
            
            npcs[npc_id] = npc
            
    except Exception as e:
        print(f"加载NPC模板失败: {e}")
        # 如果加载失败，返回空字典
        pass
    
    return npcs


@world_bp.route('/description', methods=['GET'])
def get_world_description():
    """获取世界基本描述信息"""
    try:
        world_desc = load_world_description()
        return jsonify({
            "status": "success",
            "data": world_desc
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@world_bp.route('/create', methods=['POST'])
def create_world():
    """创建游戏世界，包括分析勇者信息和生成世界基本情况，并创建游戏会话"""
    data = request.json
    player_response = data.get('playerResponse', '')

    try:
        # 获取游戏数据服务
        game_data_service = get_game_data_service()

        # 1. 从玩家输入中提取勇者信息
        hero_info = extract_hero_info(player_response)
        equipment = extract_equipment(player_response)

        # 合并信息
        base_stats = {
            "strength": hero_info["stats"]["strength"] or 50,
            "intelligence": hero_info["stats"]["intelligence"] or 50,
            "agility": hero_info["stats"]["agility"] or 50,
            "luck": hero_info["stats"]["luck"] or 50
        }

        # 应用职业加成
        from api.hero_api import _apply_profession_bonuses
        profession = hero_info.get("profession", "").lower()
        adjusted_stats = _apply_profession_bonuses(base_stats, profession)

        hero_data = {
            "basic_info": {
                "name": hero_info["name"] or "无名勇者",
                "gender": hero_info["gender"] or "未知",
                "profession": hero_info["profession"] or "勇者",
                "age": hero_info["age"] or random.randint(18, 30)
            },
            "stats": {
                "hp": 100,
                "mp": 100,
                **adjusted_stats
            },
            "equipment": equipment
        }

        # 2. 创建勇者对象
        hero = Hero(
            name=hero_data["basic_info"]["name"],
            gender=hero_data["basic_info"]["gender"],
            profession=hero_data["basic_info"]["profession"],
            age=hero_data["basic_info"]["age"]
        )

        # 更新勇者属性
        hero.stats.update(hero_data["stats"])

        # 添加装备
        for slot, item in hero_data["equipment"].items():
            if item:  # 只添加非空装备
                hero.add_equipment(slot, item)

        # 3. 生成世界基本情况
        world = generate_world_info(hero_data)
        npcs = generate_npc_info()

        # 4. 初始化游戏状态
        initial_state = {
            "day": 1,
            "player": hero.to_dict(),
            "world": world.to_dict(),
            "npc": {npc_id: npc.to_dict() for npc_id, npc in npcs.items()},
            "initialResponse": player_response
        }

        # 5. 创建游戏会话
        game_id = game_data_service.create_new_game(initial_state)

        if not game_id:
            return jsonify({"status": "error", "message": "创建游戏会话失败"}), 500

        return jsonify({
            "status": "success",
            "game_id": game_id,
            "hero": hero.to_dict(),
            "world": world.to_dict(),
            "gameState": initial_state,
            "message": "世界创建完成，游戏会话已建立"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
