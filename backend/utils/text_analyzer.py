"""
从玩家输入中提取勇者信息，调用大模型提取
"""

import os
import re
import logging
import json
from llm.chat import create_chat_completion

HERO_INFO_PROMPT_TEMPLATE = None
hero_info_prompt_template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'prompts', 'analyze_prologue_hero_info_prompt.txt')
with open(hero_info_prompt_template_path, 'r', encoding='utf-8') as file:
    HERO_INFO_PROMPT_TEMPLATE = file.read()
EQUIPMENT_PROMPT_TEMPLATE = None
equipment_prompt_template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'prompts', 'analyze_prologue_equiment_prompt.txt')
with open(equipment_prompt_template_path, 'r', encoding='utf-8') as file:
    EQUIPMENT_PROMPT_TEMPLATE = file.read()

logger = logging.getLogger(__name__)

# 提取 JSON 的函数
def extract_result_json(model_output: str) -> dict:
    match = re.search(r"<提取结果>\s*({.*?})\s*</提取结果>", model_output, re.DOTALL)
    if not match:
        raise ValueError("未找到 <提取结果> 标签中的 JSON 内容。")
    json_str = match.group(1)
    return json.loads(json_str)


def extract_hero_info(text):
    """
    从玩家输入中提取勇者信息，调用大模型进行提取
    
    参数:
        text (str): 玩家输入的文本
        
    返回:
        dict: 包含勇者信息的字典
    """
    prompt = HERO_INFO_PROMPT_TEMPLATE.format(player_input=text)
    response = create_chat_completion(prompt)
    # 从API响应中提取内容
    content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
    logger.info(f"提取勇者信息的响应内容: {content}")
    return extract_result_json(content)

def extract_equipment(text):
    """
    从玩家输入中提取装备信息，调用大模型进行提取
    
    参数:
        text (str): 玩家输入的文本
        
    返回:
        dict: 包含装备信息的字典
    """
    prompt = EQUIPMENT_PROMPT_TEMPLATE.format(player_input=text)
    response = create_chat_completion(prompt)
    # 从API响应中提取内容
    content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
    logger.info(f"提取装备信息的响应内容: {content}")
    return extract_result_json(content)



if __name__ == '__main__':
    text = "一位衣着堂皇的女子，头戴金冠，身穿华丽的长裙，手持权杖，站在教堂门前。"
    hero_info = extract_hero_info(text)
    equipment = extract_equipment(text)
    print(hero_info)
    print(equipment)
