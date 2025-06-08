"""
JSON处理工具函数
提供JSON序列化、反序列化、验证等功能
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
from dataclasses import asdict, is_dataclass

from utils.logger import get_logger

logger = get_logger(__name__)


class GameJSONEncoder(json.JSONEncoder):
    """
    自定义JSON编码器，处理游戏数据中的特殊类型
    """
    
    def default(self, obj):
        """处理特殊类型的序列化"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            return obj.total_seconds()
        elif is_dataclass(obj):
            return asdict(obj)
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return super().default(obj)


def serialize_game_data(data: Dict[str, Any]) -> str:
    """
    序列化游戏数据为JSON字符串
    
    Args:
        data (Dict[str, Any]): 游戏数据
        
    Returns:
        str: JSON字符串
    """
    try:
        json_str = json.dumps(
            data,
            cls=GameJSONEncoder,
            ensure_ascii=False,
            indent=2,
            sort_keys=True
        )
        logger.debug("游戏数据序列化成功")
        return json_str
    except Exception as e:
        logger.error(f"游戏数据序列化失败: {e}")
        raise


def deserialize_game_data(json_str: str) -> Dict[str, Any]:
    """
    反序列化JSON字符串为游戏数据
    
    Args:
        json_str (str): JSON字符串
        
    Returns:
        Dict[str, Any]: 游戏数据
    """
    try:
        data = json.loads(json_str)
        
        # 处理特殊字段的反序列化
        data = _process_datetime_fields(data)
        
        logger.debug("游戏数据反序列化成功")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析失败: {e}")
        raise
    except Exception as e:
        logger.error(f"游戏数据反序列化失败: {e}")
        raise


def _process_datetime_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理数据中的日期时间字段
    
    Args:
        data (Dict[str, Any]): 原始数据
        
    Returns:
        Dict[str, Any]: 处理后的数据
    """
    datetime_fields = ['created_at', 'last_accessed', 'expires_at', 'updated_at']
    
    for field in datetime_fields:
        if field in data and isinstance(data[field], str):
            try:
                data[field] = datetime.fromisoformat(data[field])
            except ValueError:
                logger.warning(f"无法解析日期时间字段 {field}: {data[field]}")
    
    return data


def create_game_metadata(game_id: str, initial_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    创建游戏元数据
    
    Args:
        game_id (str): 游戏ID
        initial_data (Dict[str, Any]): 初始游戏数据
        
    Returns:
        Dict[str, Any]: 包含元数据的完整游戏数据
    """
    now = datetime.now()
    expires_at = now + timedelta(days=7)
    
    metadata = {
        "game_id": game_id,
        "created_at": now,
        "last_accessed": now,
        "expires_at": expires_at,
        "updated_at": now,
        "version": "1.0",
        "data_format": "json"
    }
    
    # 合并元数据和游戏数据
    game_data = {
        "metadata": metadata,
        "game_state": initial_data
    }
    
    logger.debug(f"创建游戏元数据: {game_id}")
    return game_data


def update_game_metadata(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    更新游戏元数据
    
    Args:
        game_data (Dict[str, Any]): 游戏数据
        
    Returns:
        Dict[str, Any]: 更新后的游戏数据
    """
    if "metadata" not in game_data:
        logger.warning("游戏数据中缺少元数据")
        return game_data
    
    now = datetime.now()
    game_data["metadata"]["last_accessed"] = now
    game_data["metadata"]["updated_at"] = now
    
    logger.debug("游戏元数据更新成功")
    return game_data


def validate_game_data_structure(data: Dict[str, Any]) -> bool:
    """
    验证游戏数据结构是否正确
    
    Args:
        data (Dict[str, Any]): 游戏数据
        
    Returns:
        bool: 结构正确返回True，否则返回False
    """
    try:
        # 检查必需的顶级字段
        required_fields = ["metadata", "game_state"]
        for field in required_fields:
            if field not in data:
                logger.error(f"游戏数据缺少必需字段: {field}")
                return False
        
        # 检查元数据结构
        metadata = data["metadata"]
        required_metadata_fields = [
            "game_id", "created_at", "last_accessed", 
            "expires_at", "updated_at", "version"
        ]
        for field in required_metadata_fields:
            if field not in metadata:
                logger.error(f"元数据缺少必需字段: {field}")
                return False
        
        # 检查游戏状态结构
        game_state = data["game_state"]
        required_state_fields = ["day", "player", "world"]
        for field in required_state_fields:
            if field not in game_state:
                logger.error(f"游戏状态缺少必需字段: {field}")
                return False
        
        logger.debug("游戏数据结构验证通过")
        return True
        
    except Exception as e:
        logger.error(f"游戏数据结构验证失败: {e}")
        return False


def is_game_expired(game_data: Dict[str, Any]) -> bool:
    """
    检查游戏是否已过期
    
    Args:
        game_data (Dict[str, Any]): 游戏数据
        
    Returns:
        bool: 已过期返回True，否则返回False
    """
    try:
        if "metadata" not in game_data:
            logger.warning("游戏数据中缺少元数据，视为已过期")
            return True
        
        expires_at = game_data["metadata"].get("expires_at")
        if not expires_at:
            logger.warning("游戏数据中缺少过期时间，视为已过期")
            return True
        
        # 如果expires_at是字符串，尝试解析
        if isinstance(expires_at, str):
            try:
                expires_at = datetime.fromisoformat(expires_at)
            except ValueError:
                logger.error(f"无法解析过期时间: {expires_at}")
                return True
        
        now = datetime.now()
        is_expired = now > expires_at
        
        if is_expired:
            logger.debug(f"游戏已过期: {game_data['metadata']['game_id']}")
        
        return is_expired
        
    except Exception as e:
        logger.error(f"检查游戏过期状态失败: {e}")
        return True


def get_remaining_time(game_data: Dict[str, Any]) -> Optional[timedelta]:
    """
    获取游戏剩余有效时间
    
    Args:
        game_data (Dict[str, Any]): 游戏数据
        
    Returns:
        Optional[timedelta]: 剩余时间，已过期或错误返回None
    """
    try:
        if "metadata" not in game_data:
            return None
        
        expires_at = game_data["metadata"].get("expires_at")
        if not expires_at:
            return None
        
        # 如果expires_at是字符串，尝试解析
        if isinstance(expires_at, str):
            try:
                expires_at = datetime.fromisoformat(expires_at)
            except ValueError:
                return None
        
        now = datetime.now()
        if now > expires_at:
            return None  # 已过期
        
        remaining = expires_at - now
        return remaining
        
    except Exception as e:
        logger.error(f"获取剩余时间失败: {e}")
        return None


def format_remaining_time(remaining_time: timedelta) -> str:
    """
    格式化剩余时间为可读字符串
    
    Args:
        remaining_time (timedelta): 剩余时间
        
    Returns:
        str: 格式化的时间字符串
    """
    if remaining_time.total_seconds() <= 0:
        return "已过期"
    
    days = remaining_time.days
    hours, remainder = divmod(remaining_time.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    if days > 0:
        return f"{days}天{hours}小时{minutes}分钟"
    elif hours > 0:
        return f"{hours}小时{minutes}分钟"
    else:
        return f"{minutes}分钟"


def merge_game_state_updates(current_state: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并游戏状态更新
    
    Args:
        current_state (Dict[str, Any]): 当前游戏状态
        updates (Dict[str, Any]): 状态更新
        
    Returns:
        Dict[str, Any]: 合并后的游戏状态
    """
    try:
        # 深度复制当前状态
        import copy
        merged_state = copy.deepcopy(current_state)
        
        # 递归合并更新
        def deep_merge(target: Dict[str, Any], source: Dict[str, Any]):
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    deep_merge(target[key], value)
                else:
                    target[key] = value
        
        deep_merge(merged_state, updates)
        
        logger.debug("游戏状态合并成功")
        return merged_state
        
    except Exception as e:
        logger.error(f"游戏状态合并失败: {e}")
        raise


def extract_game_summary(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    提取游戏摘要信息
    
    Args:
        game_data (Dict[str, Any]): 完整游戏数据
        
    Returns:
        Dict[str, Any]: 游戏摘要
    """
    try:
        metadata = game_data.get("metadata", {})
        game_state = game_data.get("game_state", {})
        player = game_state.get("player", {})
        
        summary = {
            "game_id": metadata.get("game_id"),
            "created_at": metadata.get("created_at"),
            "last_accessed": metadata.get("last_accessed"),
            "expires_at": metadata.get("expires_at"),
            "current_day": game_state.get("day", 1),
            "player_name": player.get("name", "未知勇者"),
            "player_level": player.get("level", 1),
            "is_expired": is_game_expired(game_data)
        }
        
        # 添加剩余时间
        remaining_time = get_remaining_time(game_data)
        if remaining_time:
            summary["remaining_time"] = format_remaining_time(remaining_time)
        else:
            summary["remaining_time"] = "已过期"
        
        return summary
        
    except Exception as e:
        logger.error(f"提取游戏摘要失败: {e}")
        return {}
