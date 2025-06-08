"""
剧情推演相关API接口
"""

from flask import Blueprint, request, jsonify
from models import CharacterAction, LocationInfo, TimeOfDay
from llm.story_engine import create_story_progression

# 创建蓝图
story_bp = Blueprint('story', __name__)


@story_bp.route('/progress', methods=['POST'])
def progress_story():
    """进行剧情推演"""
    data = request.json
    
    try:
        # 解析输入参数
        location_data = data.get('location', {})
        character_actions_data = data.get('character_actions', [])
        world_history = data.get('world_history', [])
        current_time_str = data.get('current_time', 'D1Morning')
        current_world_state = data.get('current_world_state', {})
        current_character_states = data.get('current_character_states', {})
        
        # 创建地点信息对象
        location = LocationInfo(
            name=location_data.get('name', '未知地点'),
            description=location_data.get('description', ''),
            current_characters=location_data.get('current_characters', []),
            special_properties=location_data.get('special_properties', {})
        )
        
        # 创建角色动作对象列表
        character_actions = []
        for action_data in character_actions_data:
            action = CharacterAction(
                character_name=action_data.get('character_name', ''),
                action_description=action_data.get('action_description', ''),
                location=action_data.get('location', '')
            )
            character_actions.append(action)
        
        # 转换时间枚举
        try:
            current_time = TimeOfDay[current_time_str]
        except KeyError:
            current_time = TimeOfDay.D1Morning  # 默认值
        
        # 调用剧情推演引擎
        result = create_story_progression(
            location=location,
            character_actions=character_actions,
            world_history=world_history,
            current_time=current_time,
            current_world_state=current_world_state,
            current_character_states=current_character_states
        )
        
        return jsonify({
            "status": "success",
            "result": result.to_dict(),
            "message": "剧情推演完成"
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
