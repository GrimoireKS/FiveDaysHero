"""
游戏数据服务
提供游戏状态管理、数据操作等高级功能
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from services.session_service import get_session_service
from utils.json_utils import merge_game_state_updates
from utils.logger import get_logger

logger = get_logger(__name__)


class GameDataService:
    """游戏数据服务类"""
    
    def __init__(self):
        """初始化游戏数据服务"""
        self.session_service = get_session_service()
        logger.info("游戏数据服务初始化完成")
    
    def create_new_game(self, initial_data: Dict[str, Any]) -> Optional[str]:
        """
        创建新游戏

        Args:
            initial_data (Dict[str, Any]): 初始游戏数据

        Returns:
            Optional[str]: 成功返回游戏ID，失败返回None
        """
        logger.info("开始创建新游戏")
        logger.debug(f"初始数据键: {list(initial_data.keys())}")

        try:
            # 确保初始数据包含必需字段
            logger.debug("验证初始游戏数据")
            if not self._validate_initial_data(initial_data):
                logger.error("初始游戏数据验证失败")
                logger.debug(f"验证失败的数据: {initial_data}")
                return None

            logger.debug("初始数据验证通过")

            # 标准化初始数据
            logger.debug("标准化初始游戏数据")
            standardized_data = self._standardize_initial_data(initial_data)
            logger.debug(f"标准化后的数据键: {list(standardized_data.keys())}")

            # 创建会话
            logger.debug("调用会话服务创建会话")
            game_id = self.session_service.create_session(standardized_data)

            if game_id:
                logger.info(f"新游戏创建成功: {game_id}")
                logger.debug(f"游戏数据大小: {len(str(standardized_data))} 字符")
            else:
                logger.error("新游戏创建失败 - 会话服务返回None")

            return game_id

        except Exception as e:
            logger.error(f"创建新游戏异常: {e}")
            import traceback
            logger.debug(f"异常堆栈: {traceback.format_exc()}")
            return None
    
    def get_game_state(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        获取游戏状态

        Args:
            game_id (str): 游戏ID

        Returns:
            Optional[Dict[str, Any]]: 游戏状态，失败返回None
        """
        logger.debug(f"开始获取游戏状态: {game_id}")

        try:
            logger.debug("调用会话服务获取会话数据")
            game_data = self.session_service.get_session_data(game_id)
            if not game_data:
                logger.warning(f"会话数据为空: {game_id}")
                return None

            logger.debug(f"会话数据获取成功，数据键: {list(game_data.keys())}")

            # 返回游戏状态部分
            game_state = game_data.get("game_state", {})

            if game_state:
                logger.debug(f"游戏状态获取成功: {game_id}")
                logger.debug(f"游戏状态键: {list(game_state.keys())}")
                logger.debug(f"当前天数: {game_state.get('day', '未知')}")
            else:
                logger.warning(f"游戏状态为空: {game_id}")

            return game_state

        except Exception as e:
            logger.error(f"获取游戏状态异常 {game_id}: {e}")
            import traceback
            logger.debug(f"异常堆栈: {traceback.format_exc()}")
            return None
    
    def update_game_state(self, game_id: str, state_updates: Dict[str, Any]) -> bool:
        """
        更新游戏状态

        Args:
            game_id (str): 游戏ID
            state_updates (Dict[str, Any]): 状态更新

        Returns:
            bool: 更新成功返回True，失败返回False
        """
        logger.debug(f"开始更新游戏状态: {game_id}")
        logger.debug(f"状态更新键: {list(state_updates.keys())}")

        try:
            # 获取当前游戏数据
            logger.debug("获取当前游戏数据")
            game_data = self.session_service.get_session_data(game_id)
            if not game_data:
                logger.error(f"无法获取游戏数据: {game_id}")
                return False

            logger.debug(f"当前游戏数据获取成功，数据键: {list(game_data.keys())}")

            # 合并状态更新
            current_state = game_data.get("game_state", {})
            logger.debug(f"当前状态键: {list(current_state.keys())}")
            logger.debug("开始合并状态更新")

            updated_state = merge_game_state_updates(current_state, state_updates)
            logger.debug(f"状态合并完成，更新后状态键: {list(updated_state.keys())}")

            # 更新游戏数据
            game_data["game_state"] = updated_state
            logger.debug("游戏数据中的状态已更新")

            # 保存更新后的数据
            logger.debug("保存更新后的游戏数据")
            success = self.session_service.update_session_data(game_id, game_data)

            if success:
                logger.debug(f"游戏状态更新成功: {game_id}")
                logger.debug(f"更新后天数: {updated_state.get('day', '未知')}")
            else:
                logger.error(f"游戏状态更新失败: {game_id}")

            return success

        except Exception as e:
            logger.error(f"更新游戏状态异常 {game_id}: {e}")
            import traceback
            logger.debug(f"异常堆栈: {traceback.format_exc()}")
            return False
    
    def get_player_data(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        获取玩家数据
        
        Args:
            game_id (str): 游戏ID
            
        Returns:
            Optional[Dict[str, Any]]: 玩家数据，失败返回None
        """
        try:
            game_state = self.get_game_state(game_id)
            if not game_state:
                return None
            
            player_data = game_state.get("player", {})
            
            logger.debug(f"获取玩家数据成功: {game_id}")
            return player_data
            
        except Exception as e:
            logger.error(f"获取玩家数据异常 {game_id}: {e}")
            return None
    
    def update_player_data(self, game_id: str, player_updates: Dict[str, Any]) -> bool:
        """
        更新玩家数据
        
        Args:
            game_id (str): 游戏ID
            player_updates (Dict[str, Any]): 玩家数据更新
            
        Returns:
            bool: 更新成功返回True，失败返回False
        """
        try:
            state_updates = {"player": player_updates}
            return self.update_game_state(game_id, state_updates)
            
        except Exception as e:
            logger.error(f"更新玩家数据异常 {game_id}: {e}")
            return False
    
    def get_world_data(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        获取世界数据
        
        Args:
            game_id (str): 游戏ID
            
        Returns:
            Optional[Dict[str, Any]]: 世界数据，失败返回None
        """
        try:
            game_state = self.get_game_state(game_id)
            if not game_state:
                return None
            
            world_data = game_state.get("world", {})
            
            logger.debug(f"获取世界数据成功: {game_id}")
            return world_data
            
        except Exception as e:
            logger.error(f"获取世界数据异常 {game_id}: {e}")
            return None
    
    def update_world_data(self, game_id: str, world_updates: Dict[str, Any]) -> bool:
        """
        更新世界数据
        
        Args:
            game_id (str): 游戏ID
            world_updates (Dict[str, Any]): 世界数据更新
            
        Returns:
            bool: 更新成功返回True，失败返回False
        """
        try:
            state_updates = {"world": world_updates}
            return self.update_game_state(game_id, state_updates)
            
        except Exception as e:
            logger.error(f"更新世界数据异常 {game_id}: {e}")
            return False
    
    def get_npc_data(self, game_id: str, npc_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        获取NPC数据
        
        Args:
            game_id (str): 游戏ID
            npc_id (Optional[str]): NPC ID，为None时返回所有NPC数据
            
        Returns:
            Optional[Dict[str, Any]]: NPC数据，失败返回None
        """
        try:
            game_state = self.get_game_state(game_id)
            if not game_state:
                return None
            
            npc_data = game_state.get("npc", {})
            
            if npc_id:
                # 返回特定NPC数据
                if npc_id in npc_data:
                    result = npc_data[npc_id]
                    logger.debug(f"获取NPC数据成功: {game_id}, NPC: {npc_id}")
                    return result
                else:
                    logger.warning(f"NPC不存在: {game_id}, NPC: {npc_id}")
                    return None
            else:
                # 返回所有NPC数据
                logger.debug(f"获取所有NPC数据成功: {game_id}")
                return npc_data
            
        except Exception as e:
            logger.error(f"获取NPC数据异常 {game_id}: {e}")
            return None
    
    def update_npc_data(self, game_id: str, npc_id: str, npc_updates: Dict[str, Any]) -> bool:
        """
        更新NPC数据
        
        Args:
            game_id (str): 游戏ID
            npc_id (str): NPC ID
            npc_updates (Dict[str, Any]): NPC数据更新
            
        Returns:
            bool: 更新成功返回True，失败返回False
        """
        try:
            state_updates = {
                "npc": {
                    npc_id: npc_updates
                }
            }
            return self.update_game_state(game_id, state_updates)
            
        except Exception as e:
            logger.error(f"更新NPC数据异常 {game_id}, NPC: {npc_id}: {e}")
            return False
    
    def advance_game_day(self, game_id: str) -> bool:
        """
        推进游戏天数
        
        Args:
            game_id (str): 游戏ID
            
        Returns:
            bool: 推进成功返回True，失败返回False
        """
        try:
            game_state = self.get_game_state(game_id)
            if not game_state:
                return False
            
            current_day = game_state.get("day", 1)
            new_day = current_day + 1
            
            # 检查是否超过游戏限制（5天）
            if new_day > 5:
                logger.warning(f"游戏已达到最大天数限制: {game_id}")
                return False
            
            state_updates = {"day": new_day}
            success = self.update_game_state(game_id, state_updates)
            
            if success:
                logger.info(f"游戏天数推进成功: {game_id}, 第{new_day}天")
            else:
                logger.error(f"游戏天数推进失败: {game_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"推进游戏天数异常 {game_id}: {e}")
            return False
    
    def is_game_completed(self, game_id: str) -> bool:
        """
        检查游戏是否已完成
        
        Args:
            game_id (str): 游戏ID
            
        Returns:
            bool: 已完成返回True，否则返回False
        """
        try:
            game_state = self.get_game_state(game_id)
            if not game_state:
                return False
            
            current_day = game_state.get("day", 1)
            is_completed = current_day > 5
            
            if is_completed:
                logger.debug(f"游戏已完成: {game_id}")
            
            return is_completed
            
        except Exception as e:
            logger.error(f"检查游戏完成状态异常 {game_id}: {e}")
            return False
    
    def _validate_initial_data(self, data: Dict[str, Any]) -> bool:
        """
        验证初始游戏数据
        
        Args:
            data (Dict[str, Any]): 初始数据
            
        Returns:
            bool: 验证通过返回True，否则返回False
        """
        required_fields = ["player", "world"]
        
        for field in required_fields:
            if field not in data:
                logger.error(f"初始数据缺少必需字段: {field}")
                return False
        
        # 验证玩家数据
        player = data["player"]
        if not isinstance(player, dict):
            logger.error("初始数据中玩家信息不完整 - player不是字典")
            return False

        # 检查玩家数据结构 - 支持Hero.to_dict()的结构
        if "basic_info" in player:
            # Hero.to_dict()结构：{"basic_info": {"name": "..."}, ...}
            if not isinstance(player["basic_info"], dict) or "name" not in player["basic_info"]:
                logger.error("初始数据中玩家信息不完整 - basic_info中缺少name")
                return False
        elif "name" not in player:
            # 直接结构：{"name": "...", ...}
            logger.error("初始数据中玩家信息不完整 - 缺少name字段")
            return False
        
        # 验证世界数据
        world = data["world"]
        if not isinstance(world, dict):
            logger.error("初始数据中世界信息不完整")
            return False
        
        return True
    
    def _standardize_initial_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        标准化初始游戏数据
        
        Args:
            data (Dict[str, Any]): 原始初始数据
            
        Returns:
            Dict[str, Any]: 标准化后的数据
        """
        standardized = {
            "day": data.get("day", 1),
            "player": data["player"],
            "world": data["world"],
            "npc": data.get("npc", {}),
            "events": data.get("events", []),
            "history": data.get("history", []),
            "created_at": datetime.now().isoformat(),
            "last_action": None
        }
        
        # 确保玩家数据包含必需字段
        if "stats" not in standardized["player"]:
            standardized["player"]["stats"] = {}
        
        if "equipment" not in standardized["player"]:
            standardized["player"]["equipment"] = {}
        
        logger.debug("初始游戏数据标准化完成")
        return standardized


# 全局游戏数据服务实例
_game_data_service = None


def get_game_data_service() -> GameDataService:
    """
    获取全局游戏数据服务实例
    
    Returns:
        GameDataService: 游戏数据服务实例
    """
    global _game_data_service
    if _game_data_service is None:
        _game_data_service = GameDataService()
    return _game_data_service
