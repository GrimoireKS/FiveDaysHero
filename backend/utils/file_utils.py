"""
文件操作工具函数
提供安全的文件读写、目录管理等功能
"""

import os
import json
import shutil
import tempfile
import fcntl
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import uuid
import re

from utils.logger import get_logger

logger = get_logger(__name__)


def ensure_directory_exists(directory_path: str) -> bool:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory_path (str): 目录路径
        
    Returns:
        bool: 创建成功返回True，失败返回False
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        logger.debug(f"目录已确保存在: {directory_path}")
        return True
    except Exception as e:
        logger.error(f"创建目录失败 {directory_path}: {e}")
        return False


def generate_game_id() -> str:
    """
    生成唯一的游戏ID
    
    Returns:
        str: 格式为 game_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx 的游戏ID
    """
    game_uuid = str(uuid.uuid4())
    game_id = f"game_{game_uuid}"
    logger.debug(f"生成新的游戏ID: {game_id}")
    return game_id


def validate_game_id(game_id: str) -> bool:
    """
    验证游戏ID格式是否正确
    
    Args:
        game_id (str): 游戏ID
        
    Returns:
        bool: 格式正确返回True，否则返回False
    """
    pattern = r'^game_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    is_valid = bool(re.match(pattern, game_id))
    if not is_valid:
        logger.warning(f"无效的游戏ID格式: {game_id}")
    return is_valid


def get_game_file_path(game_id: str, base_dir: str = "backend/data/games") -> str:
    """
    获取游戏数据文件的完整路径
    
    Args:
        game_id (str): 游戏ID
        base_dir (str): 基础目录路径
        
    Returns:
        str: 游戏数据文件的完整路径
    """
    if not validate_game_id(game_id):
        raise ValueError(f"无效的游戏ID: {game_id}")
    
    filename = f"{game_id}.json"
    file_path = os.path.join(base_dir, filename)
    return file_path


def atomic_write_file(file_path: str, data: Dict[str, Any]) -> bool:
    """
    原子性写入JSON文件
    使用临时文件+重命名的方式确保写入的原子性
    
    Args:
        file_path (str): 目标文件路径
        data (Dict[str, Any]): 要写入的数据
        
    Returns:
        bool: 写入成功返回True，失败返回False
    """
    try:
        # 确保目标目录存在
        directory = os.path.dirname(file_path)
        if not ensure_directory_exists(directory):
            return False
        
        # 创建临时文件
        temp_fd, temp_path = tempfile.mkstemp(
            suffix='.tmp',
            prefix='game_',
            dir=directory
        )
        
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as temp_file:
                # 获取文件锁
                fcntl.flock(temp_file.fileno(), fcntl.LOCK_EX)
                
                # 写入数据，使用自定义编码器处理datetime等特殊类型
                from utils.json_utils import GameJSONEncoder
                json.dump(data, temp_file, ensure_ascii=False, indent=2, cls=GameJSONEncoder)
                temp_file.flush()
                os.fsync(temp_file.fileno())
            
            # 原子性重命名
            shutil.move(temp_path, file_path)
            logger.debug(f"成功原子性写入文件: {file_path}")
            return True
            
        except Exception as e:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e
            
    except Exception as e:
        logger.error(f"原子性写入文件失败 {file_path}: {e}")
        return False


def safe_read_file(file_path: str) -> Optional[Dict[str, Any]]:
    """
    安全读取JSON文件
    
    Args:
        file_path (str): 文件路径
        
    Returns:
        Optional[Dict[str, Any]]: 读取成功返回数据字典，失败返回None
    """
    try:
        if not os.path.exists(file_path):
            logger.warning(f"文件不存在: {file_path}")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as file:
            # 获取共享锁
            fcntl.flock(file.fileno(), fcntl.LOCK_SH)
            data = json.load(file)
            
        logger.debug(f"成功读取文件: {file_path}")
        return data
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误 {file_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"读取文件失败 {file_path}: {e}")
        return None


def backup_file(file_path: str, backup_dir: str = "backend/data/backups") -> bool:
    """
    备份文件到指定目录
    
    Args:
        file_path (str): 源文件路径
        backup_dir (str): 备份目录
        
    Returns:
        bool: 备份成功返回True，失败返回False
    """
    try:
        if not os.path.exists(file_path):
            logger.warning(f"源文件不存在，无法备份: {file_path}")
            return False
        
        # 创建按日期分组的备份目录
        today = datetime.now().strftime("%Y-%m-%d")
        daily_backup_dir = os.path.join(backup_dir, today)
        
        if not ensure_directory_exists(daily_backup_dir):
            return False
        
        # 生成备份文件名
        filename = os.path.basename(file_path)
        timestamp = datetime.now().strftime("%H%M%S")
        backup_filename = f"{timestamp}_{filename}"
        backup_path = os.path.join(daily_backup_dir, backup_filename)
        
        # 复制文件
        shutil.copy2(file_path, backup_path)
        logger.debug(f"文件备份成功: {file_path} -> {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"文件备份失败 {file_path}: {e}")
        return False


def delete_file(file_path: str) -> bool:
    """
    安全删除文件
    
    Args:
        file_path (str): 文件路径
        
    Returns:
        bool: 删除成功返回True，失败返回False
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"文件删除成功: {file_path}")
            return True
        else:
            logger.warning(f"文件不存在，无需删除: {file_path}")
            return True
            
    except Exception as e:
        logger.error(f"删除文件失败 {file_path}: {e}")
        return False


def get_file_age(file_path: str) -> Optional[timedelta]:
    """
    获取文件的年龄（从创建到现在的时间）
    
    Args:
        file_path (str): 文件路径
        
    Returns:
        Optional[timedelta]: 文件年龄，文件不存在返回None
    """
    try:
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        created_time = datetime.fromtimestamp(stat.st_ctime)
        age = datetime.now() - created_time
        return age
        
    except Exception as e:
        logger.error(f"获取文件年龄失败 {file_path}: {e}")
        return None


def find_expired_files(directory: str, max_age_days: int = 7) -> List[str]:
    """
    查找过期的文件
    
    Args:
        directory (str): 搜索目录
        max_age_days (int): 最大年龄（天数）
        
    Returns:
        List[str]: 过期文件路径列表
    """
    expired_files = []
    
    try:
        if not os.path.exists(directory):
            logger.warning(f"目录不存在: {directory}")
            return expired_files
        
        max_age = timedelta(days=max_age_days)
        
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            # 只处理JSON文件
            if not filename.endswith('.json'):
                continue
            
            file_age = get_file_age(file_path)
            if file_age and file_age > max_age:
                expired_files.append(file_path)
                logger.debug(f"发现过期文件: {file_path} (年龄: {file_age})")
        
        logger.info(f"在目录 {directory} 中发现 {len(expired_files)} 个过期文件")
        return expired_files
        
    except Exception as e:
        logger.error(f"查找过期文件失败 {directory}: {e}")
        return expired_files


def cleanup_expired_files(directory: str, max_age_days: int = 7, backup_before_delete: bool = True) -> int:
    """
    清理过期文件
    
    Args:
        directory (str): 搜索目录
        max_age_days (int): 最大年龄（天数）
        backup_before_delete (bool): 删除前是否备份
        
    Returns:
        int: 删除的文件数量
    """
    deleted_count = 0
    
    try:
        expired_files = find_expired_files(directory, max_age_days)
        
        for file_path in expired_files:
            try:
                # 删除前备份
                if backup_before_delete:
                    backup_file(file_path)
                
                # 删除文件
                if delete_file(file_path):
                    deleted_count += 1
                    
            except Exception as e:
                logger.error(f"删除过期文件失败 {file_path}: {e}")
        
        logger.info(f"清理完成，删除了 {deleted_count} 个过期文件")
        return deleted_count
        
    except Exception as e:
        logger.error(f"清理过期文件失败: {e}")
        return deleted_count
