"""
火山引擎ARK API聊天模块
"""

import os
import sys
import json
import requests
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# 导入日志模块
from utils.logger import get_logger

# 加载.env文件中的环境变量
load_dotenv()

# 获取日志记录器
logger = get_logger('llm.chat', level='info')


def get_api_key() -> str:
    """
    从环境变量获取 API 密钥
    
    Returns:
        str: API 密钥
    """
    # 从环境变量获取 API 密钥
    api_key = os.environ.get("ARK_API_KEY")
    
    # 如果环境变量中没有设置，记录错误并返回空字符串
    if not api_key:
        logger.error("未设置 ARK_API_KEY 环境变量。请在 .env 文件中设置此变量。")
        raise ValueError("未设置 ARK_API_KEY 环境变量。请在 .env 文件中设置此变量。")
    else:
        logger.debug("成功从环境变量获取 API 密钥")
    
    return api_key

def get_system_prompt() -> str:
    """
    从环境变量获取系统提示信息，如果不存在则使用默认值
    
    Returns:
        str: 系统提示信息
    """
    # 优先从环境变量获取系统提示信息
    system_prompt_path = os.path.join(os.path.dirname(__file__), 'resources', 'prompts', 'system_prompt.txt')
    
    logger.debug(f"尝试从路径加载系统提示: {system_prompt_path}")
    if os.path.exists(system_prompt_path):
        try:
            with open(system_prompt_path, 'r', encoding='utf-8') as file:
                system_prompt = file.read()
            logger.info(f"成功从文件加载系统提示: {system_prompt_path}")
        except Exception as e:
            logger.error(f"读取系统提示文件失败: {e}")
            system_prompt = "你是游戏的智能助手."
    else:
        logger.warning(f"系统提示文件不存在: {system_prompt_path}，使用默认提示")
        system_prompt = "你是游戏的智能助手."
    
    return system_prompt


def create_chat_completion(
    prompt: str,
    system_message: str = "",
    model: str = "ep-20250219141351-ntqmd",
    api_url: str = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
) -> Dict[str, Any]:
    """
    调用火山引擎 ARK API 创建对话完成
    
    Args:
        prompt (str): 用户提问内容
        system_message (str, optional): 系统提示信息
        model (str, optional): 模型 ID
        api_url (str, optional): API 端点 URL
    
    Returns:
        Dict[str, Any]: API 响应内容
    
    Raises:
        Exception: 当 API 调用失败时抛出异常
    """
    logger.info(f"开始创建对话完成，模型: {model}")
    logger.debug(f"用户提示: {prompt[:50]}..." if len(prompt) > 50 else f"用户提示: {prompt}")

    if not system_message:
        logger.debug("未提供系统消息，获取默认系统提示")
        system_message = get_system_prompt()

    # 准备请求负载
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
    }
    
    # 准备请求头
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {get_api_key()}'
    }
    
    try:
        # 发送请求
        logger.debug(f"发送请求到 API 端点: {api_url}")
        response = requests.post(api_url, headers=headers, json=payload)
        
        # 检查响应状态
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        logger.info("成功获取 API 响应")
        logger.info(f"响应内容: {json.dumps(result, ensure_ascii=False)[:200]}..." if len(json.dumps(result, ensure_ascii=False)) > 200 else f"响应内容: {json.dumps(result, ensure_ascii=False)}")
        
        # 返回 JSON 响应
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"API 请求失败: {e}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"状态码: {e.response.status_code}")
            logger.error(f"响应内容: {e.response.text}")
        raise
