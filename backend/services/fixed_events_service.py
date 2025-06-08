"""
固定事件服务
管理游戏中的固定事件，这些事件在特定时间必定发生
"""

import os
import json
from typing import Dict, Any, List, Optional

from models.common import TimeOfDay
from utils.logger import get_logger

logger = get_logger(__name__)


class FixedEventsService:
    """固定事件服务类"""
    
    def __init__(self):
        """初始化固定事件服务"""
        self.fixed_events = {}
        self._load_fixed_events()
        logger.info("固定事件服务初始化完成")
    
    def _load_fixed_events(self):
        """加载固定事件配置"""
        try:
            events_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'resources', 'events', 'fixed_events.json'
            )
            
            logger.debug(f"加载固定事件配置: {events_path}")
            
            with open(events_path, 'r', encoding='utf-8') as file:
                events_list = json.load(file)
            
            # 将事件列表转换为以时间为键的字典
            for event in events_list:
                event_time = event.get('event_time')
                event_description = event.get('event_description')
                
                if event_time and event_description:
                    # 验证时间枚举是否有效
                    try:
                        time_enum = TimeOfDay(event_time)
                        self.fixed_events[event_time] = {
                            'time': time_enum,
                            'description': event_description
                        }
                        logger.debug(f"加载固定事件: {event_time}")
                    except ValueError:
                        logger.warning(f"无效的事件时间: {event_time}")
                else:
                    logger.warning(f"固定事件配置不完整: {event}")
            
            logger.info(f"成功加载 {len(self.fixed_events)} 个固定事件")
            
        except FileNotFoundError:
            logger.error(f"固定事件配置文件不存在: {events_path}")
            self.fixed_events = {}
        except json.JSONDecodeError as e:
            logger.error(f"固定事件配置文件JSON格式错误: {e}")
            self.fixed_events = {}
        except Exception as e:
            logger.error(f"加载固定事件配置失败: {e}")
            self.fixed_events = {}
    
    def get_fixed_event(self, time_of_day: TimeOfDay) -> Optional[str]:
        """
        获取指定时间的固定事件
        
        Args:
            time_of_day (TimeOfDay): 时间枚举
            
        Returns:
            Optional[str]: 事件描述，如果没有固定事件则返回None
        """
        time_key = time_of_day.value
        event = self.fixed_events.get(time_key)
        
        if event:
            logger.debug(f"获取固定事件: {time_key}")
            return event['description']
        else:
            logger.debug(f"没有固定事件: {time_key}")
            return None
    
    def get_fixed_events_for_day(self, day: int) -> List[Dict[str, Any]]:
        """
        获取指定天数的所有固定事件
        
        Args:
            day (int): 天数 (1-5)
            
        Returns:
            List[Dict[str, Any]]: 该天的固定事件列表
        """
        if day < 1 or day > 5:
            logger.warning(f"无效的天数: {day}")
            return []
        
        day_events = []
        time_periods = ['Morning', 'Afternoon', 'Evening']
        
        for period in time_periods:
            time_key = f"D{day}{period}"
            event = self.fixed_events.get(time_key)
            
            if event:
                day_events.append({
                    'time': time_key,
                    'period': period.lower(),
                    'description': event['description']
                })
        
        logger.debug(f"第{day}天有 {len(day_events)} 个固定事件")
        return day_events
    
    def get_all_fixed_events(self) -> Dict[str, str]:
        """
        获取所有固定事件
        
        Returns:
            Dict[str, str]: 时间到事件描述的映射
        """
        all_events = {}
        for time_key, event in self.fixed_events.items():
            all_events[time_key] = event['description']
        
        logger.debug(f"返回所有 {len(all_events)} 个固定事件")
        return all_events
    
    def has_fixed_event(self, time_of_day: TimeOfDay) -> bool:
        """
        检查指定时间是否有固定事件
        
        Args:
            time_of_day (TimeOfDay): 时间枚举
            
        Returns:
            bool: 有固定事件返回True，否则返回False
        """
        time_key = time_of_day.value
        has_event = time_key in self.fixed_events
        
        logger.debug(f"检查固定事件 {time_key}: {has_event}")
        return has_event
    
    def get_fixed_events_summary(self) -> Dict[str, Any]:
        """
        获取固定事件摘要信息
        
        Returns:
            Dict[str, Any]: 固定事件摘要
        """
        summary = {
            'total_events': len(self.fixed_events),
            'events_by_day': {}
        }
        
        # 按天统计事件
        for day in range(1, 6):
            day_events = self.get_fixed_events_for_day(day)
            summary['events_by_day'][f'day_{day}'] = len(day_events)
        
        logger.debug("生成固定事件摘要")
        return summary
    
    def format_fixed_events_for_prompt(self, current_day: int = None) -> str:
        """
        格式化固定事件用于LLM提示
        
        Args:
            current_day (int, optional): 当前天数，如果指定则只返回该天的事件
            
        Returns:
            str: 格式化的固定事件文本
        """
        if current_day is not None:
            # 只返回指定天数的事件
            day_events = self.get_fixed_events_for_day(current_day)
            if not day_events:
                return "当天没有固定事件。"
            
            formatted_events = []
            for event in day_events:
                formatted_events.append(f"- {event['period']}: {event['description']}")
            
            return f"第{current_day}天的固定事件:\n" + "\n".join(formatted_events)
        else:
            # 返回所有固定事件
            if not self.fixed_events:
                return "没有配置固定事件。"
            
            formatted_events = []
            for day in range(1, 6):
                day_events = self.get_fixed_events_for_day(day)
                if day_events:
                    formatted_events.append(f"第{day}天:")
                    for event in day_events:
                        formatted_events.append(f"  - {event['period']}: {event['description']}")
            
            return "\n".join(formatted_events)
    
    def reload_fixed_events(self):
        """重新加载固定事件配置"""
        logger.info("重新加载固定事件配置")
        self.fixed_events = {}
        self._load_fixed_events()


# 全局固定事件服务实例
_fixed_events_service = None


def get_fixed_events_service() -> FixedEventsService:
    """
    获取全局固定事件服务实例
    
    Returns:
        FixedEventsService: 固定事件服务实例
    """
    global _fixed_events_service
    if _fixed_events_service is None:
        _fixed_events_service = FixedEventsService()
    return _fixed_events_service
