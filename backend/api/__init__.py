"""
API包初始化
包含游戏相关的所有API接口
"""

from flask import Blueprint

# 导入所有API蓝图
from .game_api import game_bp
from .hero_api import hero_bp
from .world_api import world_bp
from .story_api import story_bp
from .npc_api import npc_bp
from .events_api import events_bp


def register_blueprints(app):
    """
    注册所有API蓝图到Flask应用
    
    参数:
        app: Flask应用实例
    """
    # 注册游戏相关API
    app.register_blueprint(game_bp, url_prefix='/api/game')
    
    # 注册勇者相关API
    app.register_blueprint(hero_bp, url_prefix='/api/hero')
    
    # 注册世界相关API
    app.register_blueprint(world_bp, url_prefix='/api/world')
    
    # 注册剧情推演API
    app.register_blueprint(story_bp, url_prefix='/api/story')
    
    # 注册NPC相关API
    app.register_blueprint(npc_bp, url_prefix='/api/npcs')

    # 注册事件相关API
    app.register_blueprint(events_bp, url_prefix='/api/events')


__all__ = ['register_blueprints']
