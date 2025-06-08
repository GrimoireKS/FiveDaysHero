"""
事件相关API接口
"""

from flask import Blueprint, request, jsonify
from services import get_fixed_events_service
from models.common import TimeOfDay
from utils.logger import get_logger

logger = get_logger(__name__)

# 创建蓝图
events_bp = Blueprint('events', __name__)


@events_bp.route('/fixed', methods=['GET'])
def get_all_fixed_events():
    """获取所有固定事件"""
    try:
        logger.debug("获取所有固定事件")
        
        fixed_events_service = get_fixed_events_service()
        all_events = fixed_events_service.get_all_fixed_events()
        
        logger.debug(f"返回 {len(all_events)} 个固定事件")
        
        return jsonify({
            "status": "success",
            "events": all_events,
            "count": len(all_events),
            "message": "固定事件获取成功"
        })
        
    except Exception as e:
        logger.error(f"获取固定事件异常: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@events_bp.route('/fixed/day/<int:day>', methods=['GET'])
def get_fixed_events_for_day(day):
    """获取指定天数的固定事件"""
    try:
        logger.debug(f"获取第{day}天的固定事件")
        
        if day < 1 or day > 5:
            return jsonify({
                "status": "error", 
                "message": "天数必须在1-5之间"
            }), 400
        
        fixed_events_service = get_fixed_events_service()
        day_events = fixed_events_service.get_fixed_events_for_day(day)
        
        logger.debug(f"第{day}天有 {len(day_events)} 个固定事件")
        
        return jsonify({
            "status": "success",
            "day": day,
            "events": day_events,
            "count": len(day_events),
            "message": f"第{day}天固定事件获取成功"
        })
        
    except Exception as e:
        logger.error(f"获取第{day}天固定事件异常: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@events_bp.route('/fixed/time/<time_key>', methods=['GET'])
def get_fixed_event_by_time(time_key):
    """获取指定时间的固定事件"""
    try:
        logger.debug(f"获取时间 {time_key} 的固定事件")
        
        # 验证时间键格式
        try:
            time_enum = TimeOfDay(time_key)
        except ValueError:
            return jsonify({
                "status": "error",
                "message": f"无效的时间键: {time_key}"
            }), 400
        
        fixed_events_service = get_fixed_events_service()
        event_description = fixed_events_service.get_fixed_event(time_enum)
        has_event = fixed_events_service.has_fixed_event(time_enum)
        
        logger.debug(f"时间 {time_key} {'有' if has_event else '无'}固定事件")
        
        return jsonify({
            "status": "success",
            "time": time_key,
            "has_event": has_event,
            "event_description": event_description,
            "message": f"时间 {time_key} 事件查询成功"
        })
        
    except Exception as e:
        logger.error(f"获取时间 {time_key} 固定事件异常: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@events_bp.route('/fixed/summary', methods=['GET'])
def get_fixed_events_summary():
    """获取固定事件摘要信息"""
    try:
        logger.debug("获取固定事件摘要")
        
        fixed_events_service = get_fixed_events_service()
        summary = fixed_events_service.get_fixed_events_summary()
        
        logger.debug("固定事件摘要获取成功")
        
        return jsonify({
            "status": "success",
            "summary": summary,
            "message": "固定事件摘要获取成功"
        })
        
    except Exception as e:
        logger.error(f"获取固定事件摘要异常: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@events_bp.route('/fixed/format', methods=['GET'])
def get_formatted_fixed_events():
    """获取格式化的固定事件（用于LLM提示）"""
    try:
        current_day = request.args.get('day', type=int)
        
        logger.debug(f"获取格式化固定事件，当前天数: {current_day}")
        
        fixed_events_service = get_fixed_events_service()
        formatted_events = fixed_events_service.format_fixed_events_for_prompt(current_day)
        
        logger.debug("格式化固定事件获取成功")
        
        return jsonify({
            "status": "success",
            "formatted_events": formatted_events,
            "current_day": current_day,
            "message": "格式化固定事件获取成功"
        })
        
    except Exception as e:
        logger.error(f"获取格式化固定事件异常: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@events_bp.route('/time-enum', methods=['GET'])
def get_time_enum_values():
    """获取所有时间枚举值"""
    try:
        logger.debug("获取时间枚举值")
        
        time_values = [time_enum.value for time_enum in TimeOfDay]
        
        logger.debug(f"返回 {len(time_values)} 个时间枚举值")
        
        return jsonify({
            "status": "success",
            "time_values": time_values,
            "count": len(time_values),
            "message": "时间枚举值获取成功"
        })
        
    except Exception as e:
        logger.error(f"获取时间枚举值异常: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
