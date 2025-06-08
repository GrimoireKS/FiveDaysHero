"""
游戏行动处理服务
处理玩家行动，调用LLM进行游戏推演
"""

import os
import json
import re
from typing import Dict, Any, Optional

from llm.chat import create_chat_completion
from services.game_data_service import get_game_data_service
from services.fixed_events_service import get_fixed_events_service
from utils.logger import get_logger

logger = get_logger(__name__)


class GameActionService:
    """游戏行动处理服务类"""
    
    def __init__(self):
        """初始化游戏行动处理服务"""
        self.game_data_service = get_game_data_service()
        self.fixed_events_service = get_fixed_events_service()
        logger.info("游戏行动处理服务初始化完成")
    
    def process_player_action(self, game_id: str, player_action: str) -> Optional[Dict[str, Any]]:
        """
        处理玩家行动

        Args:
            game_id (str): 游戏ID
            player_action (str): 玩家行动描述

        Returns:
            Optional[Dict[str, Any]]: 处理结果，失败返回None
        """
        logger.info(f"开始处理玩家行动: {game_id}")
        logger.debug(f"玩家行动长度: {len(player_action)} 字符")
        logger.debug(f"玩家行动内容: {player_action}")

        try:
            # 获取当前游戏状态
            logger.debug("获取当前游戏状态")
            game_state = self.game_data_service.get_game_state(game_id)
            if not game_state:
                logger.error(f"无法获取游戏状态: {game_id}")
                return None

            logger.debug(f"游戏状态获取成功，当前第{game_state.get('day', 1)}天")
            logger.debug(f"玩家姓名: {game_state.get('player', {}).get('name', '未知')}")

            # 检查游戏是否已结束
            logger.debug("检查游戏是否已完成")
            if self.game_data_service.is_game_completed(game_id):
                logger.warning(f"游戏已完成，无法处理行动: {game_id}")
                return {"error": "游戏已完成"}

            # 构建LLM提示
            logger.debug("加载系统提示")
            system_prompt = self._load_system_prompt()
            logger.debug(f"系统提示长度: {len(system_prompt)} 字符")

            logger.debug("构建用户提示")
            user_prompt = self._build_user_prompt(game_state, player_action)
            logger.debug(f"用户提示长度: {len(user_prompt)} 字符")

            # 调用LLM
            logger.info("调用LLM进行游戏推演")
            logger.debug("发送LLM请求...")

            llm_response = create_chat_completion(
                prompt=user_prompt,
                system_message=system_prompt
            )

            logger.debug("LLM响应接收完成")
            logger.debug(f"LLM响应类型: {type(llm_response)}")

            # 解析LLM响应
            logger.debug("解析LLM响应")
            action_result = self._parse_llm_response(llm_response)
            if not action_result:
                logger.error("LLM响应解析失败")
                return None

            logger.debug("LLM响应解析成功")
            logger.debug(f"解析结果键: {list(action_result.keys())}")

            # 应用状态变化
            logger.debug("应用状态变化")
            success = self._apply_state_changes(game_id, game_state, action_result)
            if not success:
                logger.error("状态变化应用失败")
                return None

            logger.debug("状态变化应用成功")

            logger.info(f"玩家行动处理完成: {game_id}")
            return action_result

        except Exception as e:
            logger.error(f"处理玩家行动异常 {game_id}: {e}")
            import traceback
            logger.debug(f"异常堆栈: {traceback.format_exc()}")
            return None
    
    def _load_system_prompt(self) -> str:
        """加载系统提示"""
        try:
            prompt_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'resources', 'prompts', 'game_action_system_prompt.txt'
            )
            
            with open(prompt_path, 'r', encoding='utf-8') as file:
                return file.read()
                
        except Exception as e:
            logger.error(f"加载系统提示失败: {e}")
            return "你是游戏主持人，负责处理玩家行动。"
    
    def _build_user_prompt(self, game_state: Dict[str, Any], player_action: str) -> str:
        """构建用户提示"""
        logger.debug("开始构建用户提示")

        try:
            # 加载用户提示模板
            template_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'resources', 'prompts', 'game_action_user_prompt.txt'
            )

            logger.debug(f"模板路径: {template_path}")

            with open(template_path, 'r', encoding='utf-8') as file:
                template = file.read()

            logger.debug(f"模板加载成功，长度: {len(template)} 字符")

            # 提取游戏状态信息
            player = game_state.get('player', {})
            world = game_state.get('world', {})
            npcs = game_state.get('npc', {})

            logger.debug(f"玩家数据键: {list(player.keys())}")
            logger.debug(f"世界数据键: {list(world.keys())}")
            logger.debug(f"NPC数量: {len(npcs)}")

            # 格式化装备信息
            logger.debug("格式化装备信息")
            equipment_info = self._format_equipment_info(player.get('equipment', {}))
            logger.debug(f"装备信息: {equipment_info}")

            # 格式化NPC信息
            logger.debug("格式化NPC信息")
            npc_info = self._format_npc_info(npcs)
            logger.debug(f"NPC信息长度: {len(npc_info)} 字符")

            # 格式化世界信息
            logger.debug("格式化世界信息")
            world_info = self._format_world_info(world)
            logger.debug(f"世界信息长度: {len(world_info)} 字符")

            # 格式化历史事件
            logger.debug("格式化历史事件")
            history_events = self._format_history_events(game_state.get('history', []))
            logger.debug(f"历史事件数量: {len(game_state.get('history', []))}")

            # 格式化固定事件
            logger.debug("格式化固定事件")
            current_day = game_state.get('day', 1)
            fixed_events_info = self.fixed_events_service.format_fixed_events_for_prompt(current_day)
            logger.debug(f"当前天数固定事件: {len(fixed_events_info)} 字符")

            # 提取玩家基本信息和属性
            player_basic_info = player.get('basic_info', {})
            player_stats = player.get('stats', {})

            # 填充模板
            logger.debug("填充模板参数")
            prompt = template.format(
                current_day=game_state.get('day', 1),
                player_name=player_basic_info.get('name', '未知'),
                player_gender=player_basic_info.get('gender', '未知'),
                player_profession=player_basic_info.get('profession', '勇者'),
                player_age=player_basic_info.get('age', '未知'),
                player_hp=player_stats.get('hp', 100),
                player_mp=player_stats.get('mp', 100),
                player_strength=player_stats.get('strength', 50),
                player_intelligence=player_stats.get('intelligence', 50),
                player_agility=player_stats.get('agility', 50),
                player_luck=player_stats.get('luck', 50),
                equipment_info=equipment_info,
                current_time=world.get('current_time', '上午'),
                weather=world.get('weather', '晴天'),
                world_info=world_info,
                npc_info=npc_info,
                history_events=history_events,
                fixed_events_info=fixed_events_info,
                player_action=player_action
            )

            logger.debug(f"用户提示构建完成，最终长度: {len(prompt)} 字符")
            return prompt

        except Exception as e:
            logger.error(f"构建用户提示失败: {e}")
            import traceback
            logger.debug(f"异常堆栈: {traceback.format_exc()}")
            return f"玩家行动: {player_action}"
    
    def _format_equipment_info(self, equipment: Dict[str, Any]) -> str:
        """格式化装备信息"""
        if not equipment:
            return "无装备"
        
        equipment_lines = []
        for slot, item in equipment.items():
            if item:
                equipment_lines.append(f"- {slot}: {item}")
        
        return "\n".join(equipment_lines) if equipment_lines else "无装备"
    
    def _format_npc_info(self, npcs: Dict[str, Any]) -> str:
        """格式化NPC信息，包含详细信息用于LLM处理"""
        if not npcs:
            return "暂无NPC信息"

        npc_lines = []
        npc_lines.append("## 可操作的NPC列表（只能修改这些NPC的状态，不允许新增NPC）:")

        for npc_id, npc_data in npcs.items():
            name = npc_data.get('name', npc_id)
            profession = npc_data.get('profession', '未知')
            relationship = npc_data.get('relationship', 0)
            age = npc_data.get('age', '未知')
            gender = npc_data.get('gender', '未知')

            # 获取NPC属性
            stats = npc_data.get('stats', {})
            strength = stats.get('strength', 0)
            intelligence = stats.get('intelligence', 0)
            agility = stats.get('agility', 0)
            luck = stats.get('luck', 0)

            # 获取描述信息
            description = npc_data.get('description', '无描述')

            npc_lines.append(f"- **{npc_id}** ({name})")
            npc_lines.append(f"  * 职业: {profession}, 年龄: {age}, 性别: {gender}")
            npc_lines.append(f"  * 属性: 力量{strength}, 智力{intelligence}, 敏捷{agility}, 幸运{luck}")
            npc_lines.append(f"  * 关系值: {relationship} (-100到100，负数为敌对，正数为友好)")
            npc_lines.append(f"  * 描述: {description}")
            npc_lines.append("")

        npc_lines.append("**重要提醒**: 只能修改上述列表中的NPC状态，不允许创建新的NPC或修改未列出的NPC。")

        return "\n".join(npc_lines)
    
    def _format_world_info(self, world: Dict[str, Any]) -> str:
        """格式化世界信息"""
        world_lines = []
        
        # 添加地点信息
        locations = world.get('locations', {})
        if locations:
            world_lines.append("- 可访问地点:")
            for loc_id, loc_info in locations.items():
                world_lines.append(f"  * {loc_info.get('name', loc_id)}: {loc_info.get('description', '无描述')}")
        
        # 添加其他世界信息
        for key, value in world.items():
            if key not in ['current_time', 'weather', 'locations', 'current_day']:
                world_lines.append(f"- {key}: {value}")
        
        return "\n".join(world_lines) if world_lines else ""
    
    def _format_history_events(self, history: list) -> str:
        """格式化历史事件"""
        if not history:
            return "暂无历史事件"
        
        # 只显示最近的5个事件
        recent_events = history[-5:] if len(history) > 5 else history
        
        event_lines = []
        for i, event in enumerate(recent_events, 1):
            event_lines.append(f"{i}. {event}")
        
        return "\n".join(event_lines)
    
    def _parse_llm_response(self, llm_response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """解析LLM响应"""
        logger.debug("开始解析LLM响应")

        try:
            # 提取响应内容
            logger.debug("提取LLM响应内容")
            choices = llm_response.get('choices', [])
            logger.debug(f"响应选择数量: {len(choices)}")

            if not choices:
                logger.error("LLM响应中没有choices")
                return None

            message = choices[0].get('message', {})
            content = message.get('content', '')

            if not content:
                logger.error("LLM响应内容为空")
                logger.debug(f"完整响应结构: {llm_response}")
                return None

            logger.debug(f"LLM原始响应长度: {len(content)} 字符")
            logger.debug(f"LLM原始响应前500字符: {content[:500]}...")

            # 尝试提取JSON部分
            logger.debug("尝试提取JSON内容")
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                logger.debug("找到JSON代码块")
            else:
                # 如果没有代码块，尝试直接解析整个内容
                json_str = content.strip()
                logger.debug("未找到JSON代码块，尝试解析整个内容")

            logger.debug(f"待解析JSON长度: {len(json_str)} 字符")
            logger.debug(f"待解析JSON前200字符: {json_str[:200]}...")

            # 解析JSON
            logger.debug("开始JSON解析")
            result = json.loads(json_str)

            logger.debug("LLM响应解析成功")
            logger.debug(f"解析结果顶级键: {list(result.keys())}")

            # 验证必需的键
            required_keys = ['player_actions', 'time_progression', 'day_summary', 'updated_states']
            missing_keys = [key for key in required_keys if key not in result]
            if missing_keys:
                logger.warning(f"解析结果缺少必需键: {missing_keys}")

            # 验证时间推演格式
            self._validate_time_progression_format(result.get('time_progression', {}))

            # 验证NPC数据
            self._validate_npc_data(result.get('updated_states', {}).get('npcs', {}))

            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            logger.error(f"解析失败的JSON内容: {json_str[:1000]}...")
            return None
        except Exception as e:
            logger.error(f"解析LLM响应异常: {e}")
            import traceback
            logger.debug(f"异常堆栈: {traceback.format_exc()}")
            return None

    def _validate_time_progression_format(self, time_progression: Dict[str, Any]):
        """验证时间推演格式"""
        logger.debug("验证时间推演格式")

        required_periods = ['morning', 'afternoon', 'evening']

        for period in required_periods:
            if period not in time_progression:
                logger.warning(f"时间推演缺少 {period} 时段")
                continue

            period_data = time_progression[period]

            # 检查必需字段
            required_fields = ['narrative', 'location', 'weather', 'atmosphere', 'events']
            for field in required_fields:
                if field not in period_data:
                    logger.warning(f"{period} 时段缺少 {field} 字段")
                elif field == 'events':
                    # 验证事件格式
                    events = period_data[field]
                    if isinstance(events, list):
                        for i, event in enumerate(events):
                            if isinstance(event, dict):
                                # 新格式：检查事件对象
                                if 'type' not in event:
                                    logger.warning(f"{period} 时段事件 {i} 缺少 type 字段")
                                if 'description' not in event:
                                    logger.warning(f"{period} 时段事件 {i} 缺少 description 字段")
                                if 'location' not in event:
                                    logger.warning(f"{period} 时段事件 {i} 缺少 location 字段")
                            else:
                                # 旧格式：字符串事件
                                logger.debug(f"{period} 时段事件 {i} 使用旧格式（字符串）")
                    else:
                        logger.warning(f"{period} 时段的 events 不是数组格式")

        logger.debug("时间推演格式验证完成")

    def _validate_npc_data(self, npc_updates: Dict[str, Any]):
        """验证NPC数据，确保只包含预定义的NPC"""
        logger.debug("验证NPC数据")

        # 加载预定义的NPC列表
        predefined_npcs = self._get_predefined_npc_ids()
        logger.debug(f"预定义NPC列表: {predefined_npcs}")

        invalid_npcs = []
        for npc_identifier in npc_updates.keys():
            # 检查是否为预定义的NPC ID
            if npc_identifier not in predefined_npcs:
                # 检查是否为中文名称，尝试映射到NPC ID
                npc_id = self._find_npc_id_by_name(npc_identifier)
                if not npc_id:
                    invalid_npcs.append(npc_identifier)
                    logger.warning(f"发现未定义的NPC: {npc_identifier}")

        if invalid_npcs:
            logger.warning(f"LLM响应包含未定义的NPC: {invalid_npcs}")
            # 从更新数据中移除无效的NPC
            for invalid_npc in invalid_npcs:
                npc_updates.pop(invalid_npc, None)
                logger.debug(f"已移除无效NPC: {invalid_npc}")

        logger.debug("NPC数据验证完成")

    def _get_predefined_npc_ids(self) -> set:
        """获取预定义的NPC ID列表"""
        try:
            import json
            import os

            npc_template_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'resources', 'npc', 'npc_templates.json'
            )

            with open(npc_template_path, 'r', encoding='utf-8') as file:
                npc_templates = json.load(file)
                return set(npc_templates.keys())

        except Exception as e:
            logger.error(f"加载NPC模板失败: {e}")
            return set()

    def _find_npc_id_by_name(self, npc_name: str) -> Optional[str]:
        """通过中文名称查找NPC ID"""
        try:
            import json
            import os

            npc_template_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'resources', 'npc', 'npc_templates.json'
            )

            with open(npc_template_path, 'r', encoding='utf-8') as file:
                npc_templates = json.load(file)

                for npc_id, npc_data in npc_templates.items():
                    if npc_data.get('name') == npc_name:
                        return npc_id

                return None

        except Exception as e:
            logger.error(f"查找NPC ID失败: {e}")
            return None

    def _apply_state_changes(self, game_id: str, current_state: Dict[str, Any], action_result: Dict[str, Any]) -> bool:
        """应用状态变化"""
        logger.debug("开始应用状态变化")

        try:
            # 直接使用 updated_states 中的最终状态，不再重复累积 time_progression
            # 因为 updated_states 已经是LLM计算好的最终状态，包含了所有时间段的累积变化
            updated_states = action_result.get('updated_states', {})
            logger.debug(f"更新状态键: {list(updated_states.keys())}")

            # 构建状态更新
            state_updates = {}

            # 更新玩家状态
            if 'player' in updated_states:
                logger.debug("处理玩家状态更新")
                current_player = current_state.get('player', {})
                updated_player = updated_states['player']
                logger.debug(f"当前玩家状态: {current_player.get('stats', {})}")
                logger.debug(f"LLM返回的最终玩家状态: {updated_player}")

                state_updates['player'] = self._merge_player_updates(current_player, updated_player)
                logger.debug("玩家状态合并完成")

            # 更新世界状态
            if 'world' in updated_states:
                logger.debug("处理世界状态更新")
                current_world = current_state.get('world', {})
                updated_world = updated_states['world']
                logger.debug(f"当前天气: {current_world.get('weather', 'N/A')}")
                logger.debug(f"更新后天气: {updated_world.get('weather', 'N/A')}")

                state_updates['world'] = self._merge_world_updates(current_world, updated_world)
                logger.debug("世界状态合并完成")

            # 更新NPC状态
            if 'npcs' in updated_states:
                logger.debug("处理NPC状态更新")
                current_npcs = current_state.get('npc', {})
                updated_npcs = updated_states['npcs']
                logger.debug(f"当前NPC数量: {len(current_npcs)}")
                logger.debug(f"更新的NPC数量: {len(updated_npcs)}")

                state_updates['npc'] = self._merge_npc_updates(current_npcs, updated_npcs)
                logger.debug("NPC状态合并完成")

            # 添加历史记录
            logger.debug("添加历史记录")
            history = current_state.get('history', [])
            day_summary = action_result.get('day_summary', {})
            current_day = current_state.get('day', 1)

            if day_summary.get('narrative'):
                new_history_entry = f"第{current_day}天: {day_summary['narrative']}"
                history.append(new_history_entry)
                logger.debug(f"添加历史记录: {new_history_entry[:100]}...")

            state_updates['history'] = history
            logger.debug(f"历史记录总数: {len(history)}")

            # 应用更新
            logger.debug("调用游戏数据服务应用状态更新")
            logger.debug(f"状态更新键: {list(state_updates.keys())}")

            success = self.game_data_service.update_game_state(game_id, state_updates)

            if success:
                logger.debug("状态变化应用成功")
            else:
                logger.error("状态变化应用失败")

            return success

        except Exception as e:
            logger.error(f"应用状态变化异常: {e}")
            import traceback
            logger.debug(f"异常堆栈: {traceback.format_exc()}")
            return False
    
    def _merge_player_updates(self, current_player: Dict[str, Any], player_updates: Dict[str, Any]) -> Dict[str, Any]:
        """合并玩家状态更新"""
        merged = current_player.copy()

        # 更新stats
        if 'stats' not in merged:
            merged['stats'] = {}

        current_stats = merged['stats']
        for stat, value in player_updates.items():
            # 只处理英文属性名，忽略中文属性名
            if stat in ['strength', 'intelligence', 'agility', 'luck', 'hp', 'mp']:
                # updated_states 中的值是LLM计算好的最终绝对值，直接使用
                if stat in ['hp', 'mp']:
                    # hp和mp确保在0-100范围内
                    merged['stats'][stat] = max(0, min(100, value))
                else:
                    # 其他属性确保不小于0
                    merged['stats'][stat] = max(0, value)

                logger.debug(f"更新玩家属性 {stat}: {current_stats.get(stat, 'N/A')} -> {merged['stats'][stat]}")
            else:
                logger.debug(f"忽略未知属性: {stat} = {value}")

        return merged
    
    def _merge_world_updates(self, current_world: Dict[str, Any], world_updates: Dict[str, Any]) -> Dict[str, Any]:
        """合并世界状态更新"""
        merged = current_world.copy()
        merged.update(world_updates)
        return merged
    
    def _merge_npc_updates(self, current_npcs: Dict[str, Any], npc_updates: Dict[str, Any]) -> Dict[str, Any]:
        """合并NPC状态更新，只允许更新预定义的NPC"""
        merged = current_npcs.copy()

        # 获取预定义的NPC ID列表
        predefined_npcs = self._get_predefined_npc_ids()
        logger.debug(f"预定义NPC列表: {predefined_npcs}")

        # 创建中文名称到NPC ID的映射
        name_to_id_mapping = {}
        for npc_id, npc_data in current_npcs.items():
            if isinstance(npc_data, dict) and 'name' in npc_data:
                name_to_id_mapping[npc_data['name']] = npc_id

        logger.debug(f"NPC名称映射: {name_to_id_mapping}")

        for npc_identifier, npc_data in npc_updates.items():
            # 尝试通过中文名称找到对应的NPC ID
            target_npc_id = name_to_id_mapping.get(npc_identifier, npc_identifier)

            # 验证NPC是否为预定义的NPC
            if target_npc_id not in predefined_npcs:
                logger.warning(f"尝试更新未定义的NPC: {npc_identifier} (映射到: {target_npc_id})")
                logger.warning(f"忽略此NPC更新，只允许更新预定义的NPC")
                continue

            if target_npc_id in merged:
                # 更新现有NPC
                if isinstance(npc_data, dict):
                    # updated_states 中的关系值是最终绝对值，直接使用
                    merged[target_npc_id].update(npc_data)
                    if 'relationship' in npc_data:
                        current_relationship = merged[target_npc_id].get('relationship', 0)
                        final_relationship = max(-100, min(100, npc_data['relationship']))
                        merged[target_npc_id]['relationship'] = final_relationship
                        logger.debug(f"更新NPC {target_npc_id} 关系值: {current_relationship} -> {final_relationship}")
                else:
                    # 如果npc_data是关系值数字，也是最终值
                    current_relationship = merged[target_npc_id].get('relationship', 0)
                    final_relationship = max(-100, min(100, npc_data))
                    merged[target_npc_id]['relationship'] = final_relationship
                    logger.debug(f"更新NPC {target_npc_id} 关系值: {current_relationship} -> {final_relationship}")
            else:
                # 不允许创建新NPC，只记录警告
                logger.warning(f"尝试创建新NPC: {npc_identifier}，但只允许更新预定义的NPC")
                logger.warning(f"忽略此NPC创建请求")

        return merged


# 全局游戏行动服务实例
_game_action_service = None


def get_game_action_service() -> GameActionService:
    """
    获取全局游戏行动服务实例
    
    Returns:
        GameActionService: 游戏行动服务实例
    """
    global _game_action_service
    if _game_action_service is None:
        _game_action_service = GameActionService()
    return _game_action_service
