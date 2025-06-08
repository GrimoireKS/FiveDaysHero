"""
剧情推演相关的数据模型
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .common import TimeOfDay


@dataclass
class CharacterAction:
    """角色动作类"""
    character_name: str
    action_description: str
    location: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_name": self.character_name,
            "action_description": self.action_description,
            "location": self.location
        }


@dataclass
class LocationInfo:
    """地点信息类"""
    name: str
    description: str
    current_characters: List[str]
    special_properties: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "current_characters": self.current_characters,
            "special_properties": self.special_properties
        }


@dataclass
class StoryContext:
    """剧情上下文类"""
    current_time: TimeOfDay
    current_location: LocationInfo
    character_actions: List[CharacterAction]
    world_history: List[str]
    current_world_state: Dict[str, Any]
    current_character_states: Dict[str, Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_time": self.current_time.value if isinstance(self.current_time, TimeOfDay) else self.current_time,
            "current_location": self.current_location.to_dict(),
            "character_actions": [action.to_dict() for action in self.character_actions],
            "world_history": self.world_history,
            "current_world_state": self.current_world_state,
            "current_character_states": self.current_character_states
        }


@dataclass
class StoryProgressionResult:
    """剧情推演结果类"""
    updated_character_states: Dict[str, Dict[str, Any]]
    updated_world_state: Dict[str, Any]
    event_summary: str
    narrative_description: str
    relationship_changes: Dict[str, Dict[str, Any]]  # 角色关系变化
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "updated_character_states": self.updated_character_states,
            "updated_world_state": self.updated_world_state,
            "event_summary": self.event_summary,
            "narrative_description": self.narrative_description,
            "relationship_changes": self.relationship_changes
        }


class StoryEvent:
    """故事事件类"""
    
    def __init__(self, time: TimeOfDay, location: str, description: str, 
                 participants: List[str], impact_level: str = "medium"):
        """
        初始化故事事件
        
        参数:
            time (TimeOfDay): 事件发生时间
            location (str): 事件发生地点
            description (str): 事件描述
            participants (List[str]): 参与者列表
            impact_level (str): 影响级别 (low/medium/high)
        """
        self.time = time
        self.location = location
        self.description = description
        self.participants = participants
        self.impact_level = impact_level
        self.consequences = []  # 事件后果
        
    def add_consequence(self, consequence: str):
        """添加事件后果"""
        self.consequences.append(consequence)
        
    def to_dict(self) -> Dict[str, Any]:
        """将事件对象转换为字典"""
        return {
            "time": self.time.value if isinstance(self.time, TimeOfDay) else self.time,
            "location": self.location,
            "description": self.description,
            "participants": self.participants,
            "impact_level": self.impact_level,
            "consequences": self.consequences
        }
