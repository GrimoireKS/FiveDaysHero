"""
基于LLM的剧情推演引擎
"""

import os
import json
import re
import sys
from typing import Dict, List, Any, Optional

# 添加当前目录到Python路径，支持直接运行
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from .chat import create_chat_completion
    from ..models.story_models import (
        StoryContext, StoryProgressionResult, CharacterAction,
        LocationInfo, StoryEvent
    )
    from ..models.common import TimeOfDay
    from ..utils.logger import get_logger
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    from llm.chat import create_chat_completion
    from models.story_models import (
        StoryContext, StoryProgressionResult, CharacterAction,
        LocationInfo, StoryEvent
    )
    from models.common import TimeOfDay
    from utils.logger import get_logger

logger = get_logger('llm.story_engine', level='info')


class StoryEngine:
    """剧情推演引擎"""
    
    def __init__(self):
        """初始化剧情引擎"""
        self.prompt_template = self._load_prompt_template()
        
    def _load_prompt_template(self) -> str:
        """加载剧情推演提示模板"""
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'resources', 'prompts', 'story_progression_prompt.txt'
        )
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as file:
                template = file.read()
            logger.info(f"成功加载剧情推演提示模板: {prompt_path}")
            return template
        except Exception as e:
            logger.error(f"加载剧情推演提示模板失败: {e}")
            raise
    
    def _extract_result_json(self, model_output: str) -> dict:
        """从模型输出中提取JSON结果"""
        logger.debug(f"尝试从模型输出中提取JSON: {model_output[:500]}...")

        # 尝试多种格式匹配
        patterns = [
            r"<推演结果>\s*```json\s*({.*?})\s*```\s*</推演结果>",
            r"<推演结果>\s*({.*?})\s*</推演结果>",
            r"```json\s*({.*?})\s*```",
            r"({.*?})"
        ]

        for pattern in patterns:
            match = re.search(pattern, model_output, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
                logger.debug(f"找到JSON字符串: {json_str[:200]}...")
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON解析失败，尝试下一个模式: {e}")
                    continue

        logger.error("未找到有效的推演结果JSON内容")
        logger.error(f"完整模型输出: {model_output}")
        raise ValueError("未找到有效的 JSON 内容。")
    
    def _format_character_actions(self, actions: List[CharacterAction]) -> str:
        """格式化角色动作为文本"""
        if not actions:
            return "无角色动作"
        
        formatted_actions = []
        for action in actions:
            formatted_actions.append(
                f"- **{action.character_name}** 在 {action.location}: {action.action_description}"
            )
        return "\n".join(formatted_actions)
    
    def _format_world_history(self, history: List[str]) -> str:
        """格式化世界历史为文本"""
        if not history:
            return "无历史记录"
        
        # 只显示最近的几条历史记录
        recent_history = history[-5:] if len(history) > 5 else history
        formatted_history = []
        for i, event in enumerate(recent_history, 1):
            formatted_history.append(f"{i}. {event}")
        
        return "\n".join(formatted_history)
    
    def _format_character_states(self, states: Dict[str, Dict[str, Any]]) -> str:
        """格式化角色状态为文本"""
        if not states:
            return "无角色状态信息"
        
        formatted_states = []
        for char_name, state in states.items():
            stats = state.get('stats', {})
            relationship = state.get('relationship', 0)
            formatted_states.append(
                f"**{char_name}**: "
                f"HP={stats.get('hp', '?')}, MP={stats.get('mp', '?')}, "
                f"力量={stats.get('strength', '?')}, 智力={stats.get('intelligence', '?')}, "
                f"敏捷={stats.get('agility', '?')}, 幸运={stats.get('luck', '?')}, "
                f"关系值={relationship}"
            )
        
        return "\n".join(formatted_states)
    
    def progress_story(self, context: StoryContext) -> StoryProgressionResult:
        """
        进行剧情推演
        
        参数:
            context (StoryContext): 剧情上下文
            
        返回:
            StoryProgressionResult: 推演结果
        """
        logger.info("开始剧情推演")
        
        # 格式化提示内容
        prompt = self.prompt_template.format(
            current_time=context.current_time.value if isinstance(context.current_time, TimeOfDay) else context.current_time,
            location_name=context.current_location.name,
            location_description=context.current_location.description,
            current_characters=", ".join(context.current_location.current_characters),
            location_properties=json.dumps(context.current_location.special_properties, ensure_ascii=False, indent=2),
            character_actions=self._format_character_actions(context.character_actions),
            world_history=self._format_world_history(context.world_history),
            current_world_state=json.dumps(context.current_world_state, ensure_ascii=False, indent=2),
            current_character_states=self._format_character_states(context.current_character_states)
        )
        
        logger.debug(f"推演提示长度: {len(prompt)} 字符")
        
        try:
            # 调用LLM进行推演
            response = create_chat_completion(prompt)
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            logger.info("LLM推演完成，开始解析结果")
            logger.debug(f"LLM响应内容: {content[:500]}...")
            
            # 解析结果
            result_data = self._extract_result_json(content)
            
            # 创建结果对象
            result = StoryProgressionResult(
                updated_character_states=result_data.get('updated_character_states', {}),
                updated_world_state=result_data.get('updated_world_state', {}),
                event_summary=result_data.get('event_summary', ''),
                narrative_description=result_data.get('narrative_description', ''),
                relationship_changes=result_data.get('relationship_changes', {})
            )
            
            logger.info("剧情推演成功完成")
            return result
            
        except Exception as e:
            logger.error(f"剧情推演失败: {e}")
            raise


def create_story_progression(
    location: LocationInfo,
    character_actions: List[CharacterAction],
    world_history: List[str],
    current_time: TimeOfDay,
    current_world_state: Dict[str, Any],
    current_character_states: Dict[str, Dict[str, Any]]
) -> StoryProgressionResult:
    """
    便捷函数：创建剧情推演
    
    参数:
        location (LocationInfo): 当前地点信息
        character_actions (List[CharacterAction]): 角色动作列表
        world_history (List[str]): 世界历史
        current_time (TimeOfDay): 当前时间
        current_world_state (Dict): 当前世界状态
        current_character_states (Dict): 当前角色状态
        
    返回:
        StoryProgressionResult: 推演结果
    """
    # 创建剧情上下文
    context = StoryContext(
        current_time=current_time,
        current_location=location,
        character_actions=character_actions,
        world_history=world_history,
        current_world_state=current_world_state,
        current_character_states=current_character_states
    )
    
    # 创建推演引擎并执行推演
    engine = StoryEngine()
    return engine.progress_story(context)
