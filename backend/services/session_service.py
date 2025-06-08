"""
会话管理服务
提供基于游戏ID的会话管理功能
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from utils.file_utils import generate_game_id, validate_game_id
from utils.json_utils import get_remaining_time, format_remaining_time
from services.file_storage_service import get_storage_service
from utils.logger import get_logger

logger = get_logger(__name__)


class SessionService:
    """会话管理服务类"""
    
    def __init__(self):
        """初始化会话管理服务"""
        self.storage_service = get_storage_service()
        logger.info("会话管理服务初始化完成")
    
    def create_session(self, initial_game_data: Dict[str, Any]) -> Optional[str]:
        """
        创建新的游戏会话

        Args:
            initial_game_data (Dict[str, Any]): 初始游戏数据

        Returns:
            Optional[str]: 成功返回游戏ID，失败返回None
        """
        logger.info("开始创建新的游戏会话")
        logger.debug(f"初始数据键: {list(initial_game_data.keys())}")

        try:
            # 生成唯一的游戏ID
            logger.debug("生成游戏ID")
            game_id = generate_game_id()
            logger.debug(f"生成的游戏ID: {game_id}")

            # 创建游戏文件
            logger.debug("调用存储服务创建游戏文件")
            success = self.storage_service.create_game_file(game_id, initial_game_data)

            if success:
                logger.info(f"游戏会话创建成功: {game_id}")
                logger.debug(f"游戏数据大小: {len(str(initial_game_data))} 字符")
                return game_id
            else:
                logger.error(f"游戏会话创建失败: {game_id}")
                return None

        except Exception as e:
            logger.error(f"创建游戏会话异常: {e}")
            import traceback
            logger.debug(f"异常堆栈: {traceback.format_exc()}")
            return None
    
    def validate_session(self, game_id: str) -> bool:
        """
        验证游戏会话是否有效

        Args:
            game_id (str): 游戏ID

        Returns:
            bool: 有效返回True，无效返回False
        """
        logger.debug(f"验证游戏会话: {game_id}")

        try:
            # 验证游戏ID格式
            logger.debug("验证游戏ID格式")
            if not validate_game_id(game_id):
                logger.warning(f"无效的游戏ID格式: {game_id}")
                return False

            logger.debug("游戏ID格式验证通过")

            # 检查游戏文件是否存在且有效
            logger.debug("检查游戏文件是否存在")
            exists = self.storage_service.game_exists(game_id)

            if exists:
                logger.debug(f"游戏会话验证成功: {game_id}")
            else:
                logger.warning(f"游戏会话不存在或已过期: {game_id}")

            return exists

        except Exception as e:
            logger.error(f"验证游戏会话异常 {game_id}: {e}")
            import traceback
            logger.debug(f"异常堆栈: {traceback.format_exc()}")
            return False
    
    def get_session_data(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        获取游戏会话数据

        Args:
            game_id (str): 游戏ID

        Returns:
            Optional[Dict[str, Any]]: 游戏数据，失败返回None
        """
        logger.debug(f"获取游戏会话数据: {game_id}")

        try:
            # 验证会话
            logger.debug("验证会话有效性")
            if not self.validate_session(game_id):
                logger.warning(f"会话验证失败: {game_id}")
                return None

            logger.debug("会话验证通过，加载游戏文件")

            # 加载游戏数据
            game_data = self.storage_service.load_game_file(game_id)

            if game_data:
                logger.debug(f"获取游戏会话数据成功: {game_id}")
                logger.debug(f"数据键: {list(game_data.keys())}")

                # 检查元数据
                metadata = game_data.get('metadata', {})
                if metadata:
                    logger.debug(f"会话创建时间: {metadata.get('created_at', '未知')}")
                    logger.debug(f"最后访问时间: {metadata.get('last_accessed', '未知')}")

            else:
                logger.warning(f"获取游戏会话数据失败: {game_id}")

            return game_data

        except Exception as e:
            logger.error(f"获取游戏会话数据异常 {game_id}: {e}")
            import traceback
            logger.debug(f"异常堆栈: {traceback.format_exc()}")
            return None
    
    def update_session_data(self, game_id: str, game_data: Dict[str, Any]) -> bool:
        """
        更新游戏会话数据
        
        Args:
            game_id (str): 游戏ID
            game_data (Dict[str, Any]): 游戏数据
            
        Returns:
            bool: 更新成功返回True，失败返回False
        """
        try:
            if not self.validate_session(game_id):
                logger.error(f"无法更新无效的游戏会话: {game_id}")
                return False
            
            success = self.storage_service.save_game_file(game_id, game_data)
            
            if success:
                logger.debug(f"游戏会话数据更新成功: {game_id}")
            else:
                logger.error(f"游戏会话数据更新失败: {game_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"更新游戏会话数据异常 {game_id}: {e}")
            return False
    
    def delete_session(self, game_id: str) -> bool:
        """
        删除游戏会话
        
        Args:
            game_id (str): 游戏ID
            
        Returns:
            bool: 删除成功返回True，失败返回False
        """
        try:
            if not validate_game_id(game_id):
                logger.error(f"无效的游戏ID: {game_id}")
                return False
            
            success = self.storage_service.delete_game_file(game_id)
            
            if success:
                logger.info(f"游戏会话删除成功: {game_id}")
            else:
                logger.error(f"游戏会话删除失败: {game_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"删除游戏会话异常 {game_id}: {e}")
            return False
    
    def get_session_info(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        获取游戏会话信息（不包含完整游戏数据）
        
        Args:
            game_id (str): 游戏ID
            
        Returns:
            Optional[Dict[str, Any]]: 会话信息，失败返回None
        """
        try:
            if not self.validate_session(game_id):
                return None
            
            summary = self.storage_service.get_game_summary(game_id)
            
            if summary:
                logger.debug(f"获取游戏会话信息成功: {game_id}")
            else:
                logger.warning(f"获取游戏会话信息失败: {game_id}")
            
            return summary
            
        except Exception as e:
            logger.error(f"获取游戏会话信息异常 {game_id}: {e}")
            return None
    
    def list_user_sessions(self, include_expired: bool = False) -> List[Dict[str, Any]]:
        """
        列出所有用户会话
        
        Args:
            include_expired (bool): 是否包含过期会话
            
        Returns:
            List[Dict[str, Any]]: 会话信息列表
        """
        try:
            sessions = self.storage_service.list_all_games(include_expired)
            
            logger.debug(f"列出用户会话完成，共 {len(sessions)} 个会话")
            return sessions
            
        except Exception as e:
            logger.error(f"列出用户会话异常: {e}")
            return []
    
    def cleanup_expired_sessions(self) -> int:
        """
        清理过期的游戏会话
        
        Returns:
            int: 清理的会话数量
        """
        try:
            deleted_count = self.storage_service.cleanup_expired_games()
            
            logger.info(f"过期会话清理完成，删除了 {deleted_count} 个会话")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理过期会话异常: {e}")
            return 0
    
    def extend_session_expiry(self, game_id: str, additional_days: int = 7) -> bool:
        """
        延长游戏会话的有效期
        
        Args:
            game_id (str): 游戏ID
            additional_days (int): 延长的天数
            
        Returns:
            bool: 延长成功返回True，失败返回False
        """
        try:
            if not self.validate_session(game_id):
                logger.error(f"无法延长无效的游戏会话: {game_id}")
                return False
            
            game_data = self.storage_service.load_game_file(game_id)
            if not game_data:
                return False
            
            # 更新过期时间
            current_expires_at = game_data["metadata"]["expires_at"]
            if isinstance(current_expires_at, str):
                current_expires_at = datetime.fromisoformat(current_expires_at)
            
            new_expires_at = current_expires_at + timedelta(days=additional_days)
            game_data["metadata"]["expires_at"] = new_expires_at
            
            # 保存更新后的数据
            success = self.storage_service.save_game_file(game_id, game_data)
            
            if success:
                logger.info(f"游戏会话有效期延长成功: {game_id}, 延长 {additional_days} 天")
            else:
                logger.error(f"游戏会话有效期延长失败: {game_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"延长游戏会话有效期异常 {game_id}: {e}")
            return False
    
    def get_session_remaining_time(self, game_id: str) -> Optional[str]:
        """
        获取游戏会话剩余时间
        
        Args:
            game_id (str): 游戏ID
            
        Returns:
            Optional[str]: 剩余时间字符串，失败返回None
        """
        try:
            game_data = self.get_session_data(game_id)
            if not game_data:
                return None
            
            remaining_time = get_remaining_time(game_data)
            if remaining_time:
                return format_remaining_time(remaining_time)
            else:
                return "已过期"
                
        except Exception as e:
            logger.error(f"获取游戏会话剩余时间异常 {game_id}: {e}")
            return None
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """
        获取会话统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            storage_stats = self.storage_service.get_storage_stats()
            
            # 添加会话相关的统计信息
            session_stats = {
                "total_sessions": storage_stats["total_games"],
                "active_sessions": storage_stats["active_games"],
                "expired_sessions": storage_stats["expired_games"],
                "storage_usage_mb": storage_stats["storage_size_mb"],
                "oldest_session": storage_stats["oldest_game"],
                "newest_session": storage_stats["newest_game"]
            }
            
            logger.debug("会话统计信息获取成功")
            return session_stats
            
        except Exception as e:
            logger.error(f"获取会话统计信息异常: {e}")
            return {}


# 全局会话管理服务实例
_session_service = None


def get_session_service() -> SessionService:
    """
    获取全局会话管理服务实例
    
    Returns:
        SessionService: 会话管理服务实例
    """
    global _session_service
    if _session_service is None:
        _session_service = SessionService()
    return _session_service
