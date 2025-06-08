"""
NPC相关API接口
"""

import json
import os
from flask import Blueprint, request, jsonify
from models import NPC

# 创建蓝图
npc_bp = Blueprint('npc', __name__)


def generate_npc_info():
    """生成NPC信息"""
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
            
            # 设置与勇者的关系值
            npc.update_relationship(npc_data['relationship'])
            
            # 处理事件
            if 'events' in npc_data and npc_data['events']:
                npc.events = []
                for event_data in npc_data['events']:
                    from models.event_models import Event
                    event = Event(event_data['time_of_day'], event_data['description'])
                    npc.events.append(event)
            
            npcs[npc_id] = npc
            
    except Exception as e:
        print(f"加载NPC模板失败: {e}")
        # 如果加载失败，返回空字典
        pass
    
    return npcs


@npc_bp.route('/', methods=['GET'])
def get_npcs():
    """获取所有NPC信息"""
    npcs = generate_npc_info()
    
    # 将NPC对象转换为字典
    npcs_dict = {}
    for npc_id, npc in npcs.items():
        npcs_dict[npc_id] = npc.to_dict()
    
    return jsonify(npcs_dict)


@npc_bp.route('/<npc_id>', methods=['GET'])
def get_npc(npc_id):
    """获取特定NPC信息"""
    npcs = generate_npc_info()
    
    if npc_id in npcs:
        return jsonify({
            "status": "success",
            "npc": npcs[npc_id].to_dict()
        })
    else:
        return jsonify({
            "status": "error",
            "message": f"NPC '{npc_id}' 不存在"
        }), 404


@npc_bp.route('/<npc_id>/relationship', methods=['PUT'])
def update_npc_relationship(npc_id):
    """更新NPC与勇者的关系值"""
    data = request.json
    new_relationship = data.get('relationship', 0)
    
    try:
        npcs = generate_npc_info()
        
        if npc_id not in npcs:
            return jsonify({
                "status": "error",
                "message": f"NPC '{npc_id}' 不存在"
            }), 404
        
        npc = npcs[npc_id]
        old_relationship = npc.relationship
        npc.update_relationship(new_relationship)
        
        return jsonify({
            "status": "success",
            "message": f"NPC '{npc.name}' 的关系值已更新",
            "old_relationship": old_relationship,
            "new_relationship": new_relationship,
            "npc": npc.to_dict()
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
