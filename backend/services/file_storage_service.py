"""
文件存储服务
提供游戏数据的文件存储、读取、备份等功能
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from utils.file_utils import (
    ensure_directory_exists, get_game_file_path, atomic_write_file,
    safe_read_file, backup_file, delete_file, cleanup_expired_files,
    validate_game_id
)
from utils.json_utils import (
    create_game_metadata, update_game_metadata, validate_game_data_structure,
    is_game_expired, get_remaining_time, extract_game_summary
)
from utils.logger import get_logger

logger = get_logger(__name__)


class FileStorageService:
    """文件存储服务类"""
    
    def __init__(self, base_dir: str = "backend/data"):
        """
        初始化文件存储服务
        
        Args:
            base_dir (str): 基础数据目录
        """
        self.base_dir = base_dir
        self.games_dir = os.path.join(base_dir, "games")
        self.backups_dir = os.path.join(base_dir, "backups")
        self.logs_dir = os.path.join(base_dir, "logs")
        
        # 确保目录存在
        self._ensure_directories()
        
        logger.info(f"文件存储服务初始化完成，数据目录: {self.base_dir}")
    
    def _ensure_directories(self):
        """确保所有必需的目录存在"""
        directories = [self.base_dir, self.games_dir, self.backups_dir, self.logs_dir]
        for directory in directories:
            ensure_directory_exists(directory)
    
    def create_game_file(self, game_id: str, initial_data: Dict[str, Any]) -> bool:
        """
        创建新的游戏文件

        Args:
            game_id (str): 游戏ID
            initial_data (Dict[str, Any]): 初始游戏数据

        Returns:
            bool: 创建成功返回True，失败返回False
        """
        logger.debug(f"开始创建游戏文件: {game_id}")

        try:
            # 验证游戏ID
            logger.debug("验证游戏ID")
            if not validate_game_id(game_id):
                logger.error(f"无效的游戏ID: {game_id}")
                return False

            # 获取文件路径
            file_path = get_game_file_path(game_id, self.games_dir)
            logger.debug(f"游戏文件路径: {file_path}")

            # 检查文件是否已存在
            if os.path.exists(file_path):
                logger.warning(f"游戏文件已存在: {game_id}")
                return False

            logger.debug("创建游戏元数据")

            # 创建包含元数据的完整游戏数据
            game_data = create_game_metadata(game_id, initial_data)
            logger.debug(f"游戏数据创建完成，数据键: {list(game_data.keys())}")

            # 验证数据结构
            logger.debug("验证游戏数据结构")
            if not validate_game_data_structure(game_data):
                logger.error(f"游戏数据结构验证失败: {game_id}")
                return False

            logger.debug("数据结构验证通过")

            # 原子性写入文件
            logger.debug("开始原子性写入文件")
            success = atomic_write_file(file_path, game_data)

            if success:
                logger.info(f"游戏文件创建成功: {game_id}")
                logger.debug(f"文件大小: {os.path.getsize(file_path)} 字节")
            else:
                logger.error(f"游戏文件创建失败: {game_id}")

            return success

        except Exception as e:
            logger.error(f"创建游戏文件异常 {game_id}: {e}")
            import traceback
            logger.debug(f"异常堆栈: {traceback.format_exc()}")
            return False
    
    def load_game_file(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        加载游戏文件
        
        Args:
            game_id (str): 游戏ID
            
        Returns:
            Optional[Dict[str, Any]]: 游戏数据，失败返回None
        """
        try:
            if not validate_game_id(game_id):
                logger.error(f"无效的游戏ID: {game_id}")
                return None
            
            file_path = get_game_file_path(game_id, self.games_dir)
            
            # 读取文件
            game_data = safe_read_file(file_path)
            if not game_data:
                logger.warning(f"无法读取游戏文件: {game_id}")
                return None
            
            # 验证数据结构
            if not validate_game_data_structure(game_data):
                logger.error(f"游戏数据结构验证失败: {game_id}")
                return None
            
            # 检查是否过期
            if is_game_expired(game_data):
                logger.warning(f"游戏已过期: {game_id}")
                return None
            
            # 更新访问时间
            game_data = update_game_metadata(game_data)
            
            # 保存更新后的元数据
            atomic_write_file(file_path, game_data)
            
            logger.debug(f"游戏文件加载成功: {game_id}")
            return game_data
            
        except Exception as e:
            logger.error(f"加载游戏文件异常 {game_id}: {e}")
            return None
    
    def save_game_file(self, game_id: str, game_data: Dict[str, Any], backup_before_save: bool = True) -> bool:
        """
        保存游戏文件
        
        Args:
            game_id (str): 游戏ID
            game_data (Dict[str, Any]): 游戏数据
            backup_before_save (bool): 保存前是否备份
            
        Returns:
            bool: 保存成功返回True，失败返回False
        """
        try:
            if not validate_game_id(game_id):
                logger.error(f"无效的游戏ID: {game_id}")
                return False
            
            file_path = get_game_file_path(game_id, self.games_dir)
            
            # 验证数据结构
            if not validate_game_data_structure(game_data):
                logger.error(f"游戏数据结构验证失败: {game_id}")
                return False
            
            # 检查是否过期
            if is_game_expired(game_data):
                logger.warning(f"尝试保存已过期的游戏: {game_id}")
                return False
            
            # 保存前备份
            if backup_before_save and os.path.exists(file_path):
                backup_file(file_path, self.backups_dir)
            
            # 更新元数据
            game_data = update_game_metadata(game_data)
            
            # 原子性写入文件
            success = atomic_write_file(file_path, game_data)
            
            if success:
                logger.debug(f"游戏文件保存成功: {game_id}")
            else:
                logger.error(f"游戏文件保存失败: {game_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"保存游戏文件异常 {game_id}: {e}")
            return False
    
    def delete_game_file(self, game_id: str, backup_before_delete: bool = True) -> bool:
        """
        删除游戏文件
        
        Args:
            game_id (str): 游戏ID
            backup_before_delete (bool): 删除前是否备份
            
        Returns:
            bool: 删除成功返回True，失败返回False
        """
        try:
            if not validate_game_id(game_id):
                logger.error(f"无效的游戏ID: {game_id}")
                return False
            
            file_path = get_game_file_path(game_id, self.games_dir)
            
            if not os.path.exists(file_path):
                logger.warning(f"游戏文件不存在: {game_id}")
                return True
            
            # 删除前备份
            if backup_before_delete:
                backup_file(file_path, self.backups_dir)
            
            # 删除文件
            success = delete_file(file_path)
            
            if success:
                logger.info(f"游戏文件删除成功: {game_id}")
            else:
                logger.error(f"游戏文件删除失败: {game_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"删除游戏文件异常 {game_id}: {e}")
            return False
    
    def game_exists(self, game_id: str) -> bool:
        """
        检查游戏文件是否存在且有效
        
        Args:
            game_id (str): 游戏ID
            
        Returns:
            bool: 存在且有效返回True，否则返回False
        """
        try:
            if not validate_game_id(game_id):
                return False
            
            file_path = get_game_file_path(game_id, self.games_dir)
            
            if not os.path.exists(file_path):
                return False
            
            # 读取并检查数据
            game_data = safe_read_file(file_path)
            if not game_data:
                return False
            
            # 检查是否过期
            if is_game_expired(game_data):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"检查游戏文件存在性异常 {game_id}: {e}")
            return False
    
    def get_game_summary(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        获取游戏摘要信息
        
        Args:
            game_id (str): 游戏ID
            
        Returns:
            Optional[Dict[str, Any]]: 游戏摘要，失败返回None
        """
        try:
            game_data = self.load_game_file(game_id)
            if not game_data:
                return None
            
            summary = extract_game_summary(game_data)
            return summary
            
        except Exception as e:
            logger.error(f"获取游戏摘要异常 {game_id}: {e}")
            return None
    
    def list_all_games(self, include_expired: bool = False) -> List[Dict[str, Any]]:
        """
        列出所有游戏
        
        Args:
            include_expired (bool): 是否包含过期游戏
            
        Returns:
            List[Dict[str, Any]]: 游戏摘要列表
        """
        games = []
        
        try:
            if not os.path.exists(self.games_dir):
                return games
            
            for filename in os.listdir(self.games_dir):
                if not filename.endswith('.json'):
                    continue
                
                # 提取游戏ID
                game_id = filename[:-5]  # 移除.json后缀
                
                if not validate_game_id(game_id):
                    continue
                
                # 获取游戏摘要
                summary = self.get_game_summary(game_id)
                if summary:
                    # 根据参数决定是否包含过期游戏
                    if include_expired or not summary.get('is_expired', True):
                        games.append(summary)
            
            logger.debug(f"列出游戏完成，共 {len(games)} 个游戏")
            return games
            
        except Exception as e:
            logger.error(f"列出游戏异常: {e}")
            return games
    
    def cleanup_expired_games(self) -> int:
        """
        清理过期的游戏文件
        
        Returns:
            int: 清理的文件数量
        """
        try:
            deleted_count = cleanup_expired_files(
                directory=self.games_dir,
                max_age_days=7,
                backup_before_delete=True
            )
            
            logger.info(f"过期游戏清理完成，删除了 {deleted_count} 个文件")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理过期游戏异常: {e}")
            return 0
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        获取存储统计信息
        
        Returns:
            Dict[str, Any]: 存储统计信息
        """
        stats = {
            "total_games": 0,
            "active_games": 0,
            "expired_games": 0,
            "storage_size_mb": 0,
            "oldest_game": None,
            "newest_game": None
        }
        
        try:
            games = self.list_all_games(include_expired=True)
            stats["total_games"] = len(games)
            
            active_games = [g for g in games if not g.get('is_expired', True)]
            expired_games = [g for g in games if g.get('is_expired', False)]
            
            stats["active_games"] = len(active_games)
            stats["expired_games"] = len(expired_games)
            
            # 计算存储大小
            total_size = 0
            if os.path.exists(self.games_dir):
                for filename in os.listdir(self.games_dir):
                    file_path = os.path.join(self.games_dir, filename)
                    if os.path.isfile(file_path):
                        total_size += os.path.getsize(file_path)
            
            stats["storage_size_mb"] = round(total_size / (1024 * 1024), 2)
            
            # 找到最老和最新的游戏
            if games:
                games_by_created = sorted(games, key=lambda x: x.get('created_at', datetime.min))
                stats["oldest_game"] = games_by_created[0].get('game_id')
                stats["newest_game"] = games_by_created[-1].get('game_id')
            
            logger.debug("存储统计信息获取成功")
            return stats
            
        except Exception as e:
            logger.error(f"获取存储统计信息异常: {e}")
            return stats


# 全局文件存储服务实例
_storage_service = None


def get_storage_service() -> FileStorageService:
    """
    获取全局文件存储服务实例
    
    Returns:
        FileStorageService: 文件存储服务实例
    """
    global _storage_service
    if _storage_service is None:
        _storage_service = FileStorageService()
    return _storage_service
