"""
游戏相关API接口
"""

import os
from datetime import datetime
from flask import Blueprint, request, jsonify
from services import get_game_data_service, get_session_service, get_game_action_service

# 创建蓝图
game_bp = Blueprint('game', __name__)


@game_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({"status": "ok", "message": "服务正常运行"})


@game_bp.route('/action', methods=['POST'])
def process_game_action():
    """处理玩家的游戏行动"""
    from utils.logger import get_logger
    logger = get_logger(__name__)

    logger.info("收到游戏行动处理请求")
    logger.debug(f"请求时间: {datetime.now().isoformat()}")
    logger.debug(f"请求来源IP: {request.remote_addr}")

    data = request.json
    game_id = data.get('game_id', '')
    player_action = data.get('action', '')

    logger.debug(f"请求参数 - 游戏ID: {game_id}")
    logger.debug(f"请求参数 - 行动长度: {len(player_action)} 字符")
    logger.debug(f"请求参数 - 行动内容: {player_action[:200]}..." if len(player_action) > 200 else f"请求参数 - 行动内容: {player_action}")
    logger.debug(f"请求体大小: {len(str(data))} 字符")

    try:
        # 验证必需参数
        logger.debug("验证请求参数")
        if not game_id:
            logger.warning("请求缺少游戏ID")
            return jsonify({"status": "error", "message": "缺少游戏ID"}), 400

        if not player_action:
            logger.warning("请求缺少玩家行动描述")
            return jsonify({"status": "error", "message": "缺少玩家行动描述"}), 400

        logger.debug("请求参数验证通过")

        # 验证游戏会话
        logger.debug("验证游戏会话")
        session_service = get_session_service()
        if not session_service.validate_session(game_id):
            logger.warning(f"游戏会话验证失败: {game_id}")
            return jsonify({"status": "error", "message": "游戏会话不存在或已过期"}), 404

        logger.debug("游戏会话验证通过")

        # 处理玩家行动
        logger.info(f"开始处理玩家行动: {game_id}")
        logger.debug(f"行动处理开始时间: {datetime.now().isoformat()}")

        import time
        start_time = time.time()

        game_action_service = get_game_action_service()
        action_result = game_action_service.process_player_action(game_id, player_action)

        end_time = time.time()
        processing_time = end_time - start_time
        logger.info(f"行动处理耗时: {processing_time:.2f}秒")
        logger.debug(f"行动处理结束时间: {datetime.now().isoformat()}")

        if not action_result:
            logger.error(f"行动处理失败: {game_id}")
            return jsonify({"status": "error", "message": "行动处理失败"}), 500

        # 检查是否有错误
        if "error" in action_result:
            logger.warning(f"行动处理返回错误: {action_result['error']}")
            return jsonify({"status": "error", "message": action_result["error"]}), 400

        logger.debug("行动处理成功，获取更新后的游戏状态")
        logger.debug(f"行动结果键: {list(action_result.keys())}")

        # 获取更新后的游戏状态
        game_data_service = get_game_data_service()
        updated_game_state = game_data_service.get_game_state(game_id)

        logger.info(f"游戏行动处理完成: {game_id}")
        logger.debug(f"总处理时间: {processing_time:.2f}秒")

        return jsonify({
            "status": "success",
            "result": action_result,
            "updated_game_state": updated_game_state,
            "message": "行动处理完成"
        })

    except Exception as e:
        logger.error(f"游戏行动处理异常: {e}")
        import traceback
        logger.debug(f"异常堆栈: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": str(e)}), 500


@game_bp.route('/session/create', methods=['POST'])
def create_game_session():
    """创建新的游戏会话"""
    from utils.logger import get_logger
    logger = get_logger(__name__)

    logger.info("收到创建游戏会话请求")

    try:
        data = request.json or {}
        initial_game_data = data.get('initial_data', {})

        # 如果没有提供初始数据，使用默认数据
        if not initial_game_data:
            initial_game_data = {
                "day": 1,
                "player": {
                    "name": "勇者",
                    "stats": {"strength": 5, "intelligence": 5, "charisma": 5},
                    "inventory": []
                },
                "world": {
                    "weather": "晴天",
                    "villageStatus": "平静",
                    "npcRelations": {}
                }
            }

        logger.debug(f"初始数据键: {list(initial_game_data.keys())}")

        # 创建游戏会话
        game_data_service = get_game_data_service()
        game_id = game_data_service.create_new_game(initial_game_data)

        if not game_id:
            logger.error("游戏会话创建失败")
            return jsonify({"status": "error", "message": "创建游戏会话失败"}), 500

        logger.info(f"游戏会话创建成功: {game_id}")

        return jsonify({
            "status": "success",
            "game_id": game_id,
            "initial_data": initial_game_data,
            "message": "游戏会话创建成功"
        })

    except Exception as e:
        logger.error(f"创建游戏会话异常: {e}")
        import traceback
        logger.debug(f"异常堆栈: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": str(e)}), 500


@game_bp.route('/new', methods=['POST'])
def create_new_game():
    """创建新游戏（已弃用，请使用 /session/create）"""
    data = request.json
    player_name = data.get('playerName', '勇者')

    # 初始化游戏状态
    initial_state = {
        "day": 1,
        "player": {
            "name": player_name,
            "stats": {"strength": 5, "intelligence": 5, "charisma": 5},
            "inventory": []
        },
        "world": {
            "weather": "晴天",
            "villageStatus": "平静",
            "npcRelations": {}
        }
    }

    return jsonify({"status": "success", "gameState": initial_state})


@game_bp.route('/prologue', methods=['GET'])
def get_prologue():
    """获取游戏开场白"""
    try:
        # 从文件中读取开场白文本
        prologue_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'resources', 'prompts', 'prologue.txt'
        )
        with open(prologue_path, 'r', encoding='utf-8') as file:
            prologue_text = file.read()
        
        return jsonify({"status": "success", "prologue": prologue_text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@game_bp.route('/start', methods=['POST'])
def start_game():
    """处理玩家对开场白的响应，开始游戏"""
    data = request.json
    player_response = data.get('playerResponse', '')

    try:
        # 这个接口现在只是简单地接收玩家响应，实际的游戏初始化由create_world接口完成
        # player_response 将在未来版本中使用
        return jsonify({
            "status": "success",
            "message": "已接收玩家响应",
            "received_response": bool(player_response)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@game_bp.route('/session/<game_id>', methods=['GET'])
def get_game_session(game_id):
    """获取游戏会话信息"""
    try:
        session_service = get_session_service()

        # 验证会话
        if not session_service.validate_session(game_id):
            return jsonify({"status": "error", "message": "游戏会话不存在或已过期"}), 404

        # 获取会话信息
        session_info = session_service.get_session_info(game_id)
        if not session_info:
            return jsonify({"status": "error", "message": "获取会话信息失败"}), 500

        return jsonify({
            "status": "success",
            "session_info": session_info,
            "message": "会话信息获取成功"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@game_bp.route('/session/<game_id>/state', methods=['GET'])
def get_game_state(game_id):
    """获取游戏状态"""
    try:
        game_data_service = get_game_data_service()

        # 获取游戏状态
        game_state = game_data_service.get_game_state(game_id)
        if not game_state:
            return jsonify({"status": "error", "message": "游戏状态不存在或已过期"}), 404

        return jsonify({
            "status": "success",
            "game_state": game_state,
            "message": "游戏状态获取成功"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@game_bp.route('/session/<game_id>/state', methods=['PUT'])
def update_game_state(game_id):
    """更新游戏状态"""
    try:
        data = request.json
        state_updates = data.get('state_updates', {})

        game_data_service = get_game_data_service()

        # 更新游戏状态
        success = game_data_service.update_game_state(game_id, state_updates)
        if not success:
            return jsonify({"status": "error", "message": "游戏状态更新失败"}), 500

        return jsonify({
            "status": "success",
            "message": "游戏状态更新成功"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@game_bp.route('/sessions', methods=['GET'])
def list_game_sessions():
    """列出所有游戏会话"""
    try:
        include_expired = request.args.get('include_expired', 'false').lower() == 'true'

        session_service = get_session_service()
        sessions = session_service.list_user_sessions(include_expired)

        return jsonify({
            "status": "success",
            "sessions": sessions,
            "count": len(sessions),
            "message": "会话列表获取成功"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@game_bp.route('/session/<game_id>', methods=['DELETE'])
def delete_game_session(game_id):
    """删除游戏会话"""
    try:
        session_service = get_session_service()

        success = session_service.delete_session(game_id)
        if not success:
            return jsonify({"status": "error", "message": "删除游戏会话失败"}), 500

        return jsonify({
            "status": "success",
            "message": "游戏会话删除成功"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@game_bp.route('/session/<game_id>/advance-day', methods=['POST'])
def advance_game_day(game_id):
    """推进游戏天数"""
    from utils.logger import get_logger
    logger = get_logger(__name__)

    logger.info(f"收到推进游戏天数请求: {game_id}")

    try:
        # 验证游戏会话
        session_service = get_session_service()
        if not session_service.validate_session(game_id):
            logger.warning(f"游戏会话验证失败: {game_id}")
            return jsonify({"status": "error", "message": "游戏会话不存在或已过期"}), 404

        # 推进天数
        game_data_service = get_game_data_service()
        success = game_data_service.advance_game_day(game_id)

        if not success:
            logger.error(f"推进游戏天数失败: {game_id}")
            return jsonify({"status": "error", "message": "推进游戏天数失败"}), 500

        # 获取更新后的游戏状态
        updated_game_state = game_data_service.get_game_state(game_id)
        current_day = updated_game_state.get("day", 1) if updated_game_state else 1

        logger.info(f"游戏天数推进成功: {game_id}, 当前第{current_day}天")

        return jsonify({
            "status": "success",
            "current_day": current_day,
            "updated_game_state": updated_game_state,
            "message": f"游戏推进到第{current_day}天"
        })

    except Exception as e:
        logger.error(f"推进游戏天数异常: {e}")
        import traceback
        logger.debug(f"异常堆栈: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": str(e)}), 500


@game_bp.route('/session/<game_id>/time-info', methods=['GET'])
def get_game_time_info(game_id):
    """获取游戏时间信息"""
    try:
        # 验证游戏会话
        session_service = get_session_service()
        if not session_service.validate_session(game_id):
            return jsonify({"status": "error", "message": "游戏会话不存在或已过期"}), 404

        # 获取游戏状态
        game_data_service = get_game_data_service()
        game_state = game_data_service.get_game_state(game_id)

        if not game_state:
            return jsonify({"status": "error", "message": "获取游戏状态失败"}), 500

        current_day = game_state.get("day", 1)
        world_state = game_state.get("world", {})
        current_time = world_state.get("current_time", "上午")

        # 计算游戏进度
        progress_percentage = min((current_day / 5) * 100, 100)

        time_info = {
            "current_day": current_day,
            "current_time": current_time,
            "max_days": 5,
            "progress_percentage": progress_percentage,
            "is_final_day": current_day >= 5
        }

        return jsonify({
            "status": "success",
            "time_info": time_info,
            "message": "游戏时间信息获取成功"
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@game_bp.route('/session/<game_id>/relationships', methods=['GET'])
def get_relationships(game_id):
    """获取游戏中的角色关系"""
    try:
        # 验证游戏会话
        session_service = get_session_service()
        if not session_service.validate_session(game_id):
            return jsonify({"status": "error", "message": "游戏会话不存在或已过期"}), 404

        # 获取游戏状态
        game_data_service = get_game_data_service()
        game_state = game_data_service.get_game_state(game_id)

        if not game_state:
            return jsonify({"status": "error", "message": "获取游戏状态失败"}), 500

        # 获取NPC数据和关系信息
        npc_data = game_state.get("npc", {})
        relationships = {}

        # 从NPC数据中提取关系值
        for npc_id, npc_info in npc_data.items():
            npc_name = npc_info.get("name", npc_id)
            relationship_value = npc_info.get("relationship", 0)
            relationships[npc_name] = relationship_value

        return jsonify({
            "status": "success",
            "relationships": relationships,
            "count": len(relationships),
            "message": "角色关系获取成功"
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@game_bp.route('/session/<game_id>/relationships/<character_name>', methods=['PUT'])
def update_relationship(game_id, character_name):
    """更新角色关系值"""
    from utils.logger import get_logger
    logger = get_logger(__name__)

    try:
        data = request.json
        new_relationship = data.get('relationship', 0)

        # 验证关系值范围
        if not isinstance(new_relationship, (int, float)) or new_relationship < -100 or new_relationship > 100:
            return jsonify({
                "status": "error",
                "message": "关系值必须是-100到100之间的数字"
            }), 400

        # 验证游戏会话
        session_service = get_session_service()
        if not session_service.validate_session(game_id):
            return jsonify({"status": "error", "message": "游戏会话不存在或已过期"}), 404

        # 获取游戏状态
        game_data_service = get_game_data_service()
        game_state = game_data_service.get_game_state(game_id)

        if not game_state:
            return jsonify({"status": "error", "message": "获取游戏状态失败"}), 500

        # 查找对应的NPC
        npc_data = game_state.get("npc", {})
        target_npc_id = None
        old_relationship = 0

        for npc_id, npc_info in npc_data.items():
            if npc_info.get("name") == character_name:
                target_npc_id = npc_id
                old_relationship = npc_info.get("relationship", 0)
                break

        if not target_npc_id:
            return jsonify({
                "status": "error",
                "message": f"角色 '{character_name}' 不存在"
            }), 404

        # 更新关系值
        state_updates = {
            "npc": {
                target_npc_id: {
                    "relationship": int(new_relationship)
                }
            }
        }

        success = game_data_service.update_game_state(game_id, state_updates)

        if not success:
            return jsonify({"status": "error", "message": "更新关系值失败"}), 500

        logger.info(f"角色关系更新成功: {game_id}, {character_name}: {old_relationship} -> {new_relationship}")

        return jsonify({
            "status": "success",
            "character_name": character_name,
            "old_relationship": old_relationship,
            "new_relationship": int(new_relationship),
            "message": f"角色 '{character_name}' 的关系值已更新"
        })

    except Exception as e:
        logger.error(f"更新角色关系异常: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@game_bp.route('/session/<game_id>/status', methods=['GET'])
def get_game_status(game_id):
    """获取游戏状态和结束检查"""
    try:
        # 验证游戏会话
        session_service = get_session_service()
        if not session_service.validate_session(game_id):
            return jsonify({"status": "error", "message": "游戏会话不存在或已过期"}), 404

        # 获取游戏状态
        game_data_service = get_game_data_service()
        game_state = game_data_service.get_game_state(game_id)

        if not game_state:
            return jsonify({"status": "error", "message": "获取游戏状态失败"}), 500

        current_day = game_state.get("day", 1)
        world_state = game_state.get("world", {})
        player_state = game_state.get("player", {})

        # 检查游戏是否结束
        is_game_over = current_day > 5
        is_final_day = current_day == 5

        # 计算游戏进度
        progress_percentage = min((current_day / 5) * 100, 100)

        # 检查玩家状态
        player_hp = player_state.get("stats", {}).get("hp", 100)
        is_player_alive = player_hp > 0

        game_status = {
            "current_day": current_day,
            "max_days": 5,
            "is_game_over": is_game_over,
            "is_final_day": is_final_day,
            "is_player_alive": is_player_alive,
            "progress_percentage": progress_percentage,
            "game_phase": "结束" if is_game_over else ("最后一天" if is_final_day else "进行中")
        }

        return jsonify({
            "status": "success",
            "game_status": game_status,
            "current_state": {
                "day": current_day,
                "player_hp": player_hp,
                "world": world_state
            },
            "message": "游戏状态获取成功"
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@game_bp.route('/session/<game_id>/ending', methods=['GET'])
def get_game_ending(game_id):
    """获取游戏结局信息"""
    try:
        # 验证游戏会话
        session_service = get_session_service()
        if not session_service.validate_session(game_id):
            return jsonify({"status": "error", "message": "游戏会话不存在或已过期"}), 404

        # 获取游戏状态
        game_data_service = get_game_data_service()
        game_state = game_data_service.get_game_state(game_id)

        if not game_state:
            return jsonify({"status": "error", "message": "获取游戏状态失败"}), 500

        current_day = game_state.get("day", 1)

        # 检查游戏是否已结束
        if current_day <= 5:
            return jsonify({
                "status": "error",
                "message": "游戏尚未结束，无法获取结局信息"
            }), 400

        # 分析游戏结局
        player_state = game_state.get("player", {})
        npc_data = game_state.get("npc", {})

        # 计算平均关系值
        total_relationships = 0
        relationship_count = 0
        for npc_info in npc_data.values():
            relationship = npc_info.get("relationship", 0)
            total_relationships += relationship
            relationship_count += 1

        avg_relationship = total_relationships / relationship_count if relationship_count > 0 else 0

        # 确定结局类型
        player_hp = player_state.get("stats", {}).get("hp", 100)

        if player_hp <= 0:
            ending_type = "失败结局"
            ending_description = "勇者在冒险中不幸牺牲..."
        elif avg_relationship >= 50:
            ending_type = "完美结局"
            ending_description = "勇者赢得了所有人的信任和爱戴，成为了真正的英雄！"
        elif avg_relationship >= 0:
            ending_type = "普通结局"
            ending_description = "勇者完成了基本的任务，获得了村民们的认可。"
        else:
            ending_type = "糟糕结局"
            ending_description = "勇者的行为让村民们感到失望..."

        ending_info = {
            "ending_type": ending_type,
            "ending_description": ending_description,
            "final_stats": {
                "days_survived": current_day - 1,
                "final_hp": player_hp,
                "average_relationship": round(avg_relationship, 1),
                "total_npcs": relationship_count
            }
        }

        return jsonify({
            "status": "success",
            "ending_info": ending_info,
            "message": "游戏结局信息获取成功"
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



