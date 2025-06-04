from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import time
import random
from dotenv import load_dotenv
from utils.text_analyzer import extract_hero_info, extract_equipment
from models import World, Hero, NPC

# 加载环境变量
load_dotenv()

app = Flask(__name__)
# 配置CORS，允许所有来源的请求
CORS(app, resources={r"/*": {"origins": "*"}})

# 配置火山引擎ARK API（需要在.env文件中设置相关密钥）
# ARK_API_KEY = os.getenv("ARK_API_KEY")

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "服务正常运行"})

@app.route('/api/game/action', methods=['POST'])
def process_game_action():
    """处理玩家的游戏行动"""
    data = request.json
    player_action = data.get('action', '')
    game_day = data.get('day', 1)
    game_state = data.get('gameState', {})
    
    # TODO: 实现与火山引擎ARK的集成，处理玩家行动
    
    # 模拟响应
    response = {
        "status": "success",
        "result": {
            "narrative": f"你在第{game_day}天执行了: {player_action}",
            "stateChanges": {
                "playerStats": {"strength": 10, "intelligence": 10},
                "worldState": {"weather": "晴天", "villageStatus": "平静"}
            },
            "events": ["村民对你的到来表示欢迎"]
        }
    }
    
    return jsonify(response)

@app.route('/api/game/new', methods=['POST'])
def create_new_game():
    """创建新游戏"""
    data = request.json
    player_name = data.get('playerName', '勇者')
    
    # 初始化游戏状态
    initial_state = {
        "day": 1,
        "player": {
            "name": player_name,
            "stats": {"strength": 5, "intelligence": 5, "charisma": 5},
            "inventory": []
        },
        "world": {
            "weather": "晴天",
            "villageStatus": "平静",
            "npcRelations": {}
        }
    }
    
    return jsonify({"status": "success", "gameState": initial_state})

@app.route('/api/game/prologue', methods=['GET'])
def get_prologue():
    """获取游戏开场白"""
    try:
        # 从文件中读取开场白文本
        prologue_path = os.path.join(os.path.dirname(__file__), 'resources', 'prompts', 'prologue.txt')
        with open(prologue_path, 'r', encoding='utf-8') as file:
            prologue_text = file.read()
        
        return jsonify({"status": "success", "prologue": prologue_text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/game/start', methods=['POST'])
def start_game():
    """处理玩家对开场白的响应，开始游戏"""
    data = request.json
    player_response = data.get('playerResponse', '')
    
    try:
        # 这个接口现在只是简单地接收玩家响应，实际的游戏初始化由create_world接口完成
        return jsonify({"status": "success", "message": "已接收玩家响应"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def generate_world_info(hero_data):
    """根据勇者信息生成世界基本情况"""
    # 这个函数将根据勇者的信息生成世界的基本情况
    # TODO: 实现与火山引擎ARK的集成，根据勇者信息生成世界设定
    
    # 创建世界对象
    world = World(
        current_day=1,
        current_time="上午",
        weather=random.choice(["晴天", "雨天"])
    )
    
    # 添加一些初始地点
    world.add_location("village", {"name": "村庄", "description": "一个平静的小村庄"})
    world.add_location("castle", {"name": "城堡", "description": "王国的中心城堡"})
    
    return world


def generate_npc_info():
    """生成NPC信息，基于resources/npc里的npc设定"""
    
    npcs = {}
    
    try:
        # 读取NPC模板文件
        npc_template_path = os.path.join(os.path.dirname(__file__), 'resources', 'npc', 'npc_templates.json')
        
        if os.path.exists(npc_template_path):
            with open(npc_template_path, 'r', encoding='utf-8') as f:
                npc_templates = json.load(f)
                
            # 根据模板创建NPC对象
            for npc_id, npc_data in npc_templates.items():
                npc = NPC(
                    name=npc_data['name'],
                    age=npc_data['age'],
                    gender=npc_data['gender'],
                    profession=npc_data['profession']
                )
                
                # 设置NPC属性
                for stat_name, stat_value in npc_data['stats'].items():
                    npc.update_stats(stat_name, stat_value)
                
                # 设置与勇者的关系值
                npc.update_relationship(npc_data['relationship'])
                
                # 处理事件
                if 'events' in npc_data and npc_data['events']:
                    npc.events = []
                    for event_data in npc_data['events']:
                        from models.event_models import Event
                        event = Event(event_data['time_of_day'], event_data['description'])
                        npc.events.append(event)
                
                # 将NPC添加到字典中
                npcs[npc_id] = npc
        else:
            # 如果模板文件不存在，创建一些默认NPC
            king = NPC(name="国王", age=60, gender="男", profession="国王")
            king.update_stats("strength", 40)
            king.update_stats("intelligence", 75)
            king.update_stats("agility", 30)
            king.update_stats("luck", 50)
            npcs["king"] = king
            
            village_elder = NPC(name="村长", age=65, gender="男", profession="村长")
            village_elder.update_stats("strength", 30)
            village_elder.update_stats("intelligence", 65)
            village_elder.update_stats("agility", 25)
            village_elder.update_stats("luck", 45)
            npcs["village_elder"] = village_elder
    
    except Exception as e:
        print(f"生成NPC信息时出错: {str(e)}")
        # 出错时创建一个默认NPC
        default_npc = NPC(name="村民", age=30, gender="男", profession="村民")
        npcs["villager"] = default_npc
    
    return npcs


@app.route('/api/world/create', methods=['POST'])
def create_world():
    """创建游戏世界，包括分析勇者信息和生成世界基本情况"""
    data = request.json
    player_response = data.get('playerResponse', '')
    
    try:
        # 1. 从玩家输入中提取勇者信息
        hero_info = extract_hero_info(player_response)
        equipment = extract_equipment(player_response)
        
        # 合并信息
        hero_data = {
            "basic_info": {
                "name": hero_info["name"] or "无名勇者",
                "gender": hero_info["gender"] or "未知",
                "profession": hero_info["profession"] or "勇者",
                "age": hero_info["age"] or random.randint(18, 30)
            },
            "stats": {
                "hp": 100,
                "mp": 100,
                "strength": hero_info["stats"]["strength"],
                "intelligence": hero_info["stats"]["intelligence"],
                "agility": hero_info["stats"]["agility"],
                "luck": hero_info["stats"]["luck"]
            },
            "equipment": equipment
        }
        
        # 2. 生成世界基本情况
        world = generate_world_info(hero_data)
        npcs = generate_npc_info()
        
        # 3. 初始化游戏状态
        initial_state = {
            "day": 1,
            "player": hero.to_dict(),
            "world": world.to_dict(),
            "npc": {npc_id: npc.to_dict() for npc_id, npc in npcs.items()},
            "initialResponse": player_response
        }
        
        return jsonify({
            "status": "success", 
            "hero": hero.to_dict(),
            "world": world.to_dict(),
            "gameState": initial_state,
            "message": "世界创建完成"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/hero/analyze', methods=['POST'])
def analyze_hero():
    """分析玩家输入，提取勇者信息"""
    data = request.json
    player_response = data.get('playerResponse', '')
    
    try:
        # 从玩家输入中提取勇者信息
        hero_info = extract_hero_info(player_response)
        equipment = extract_equipment(player_response)
        
        # 创建勇者对象
        hero = Hero(
            name=hero_info["name"] or "无名勇者",
            gender=hero_info["gender"] or "未知",
            profession=hero_info["profession"] or "勇者",
            age=hero_info["age"] or random.randint(18, 30)
        )
        
        # 更新勇者属性
        hero.stats["strength"] = hero_info["stats"]["strength"]
        hero.stats["intelligence"] = hero_info["stats"]["intelligence"]
        hero.stats["agility"] = hero_info["stats"]["agility"]
        hero.stats["luck"] = hero_info["stats"]["luck"]
        
        # 添加装备
        for slot, item in equipment.items():
            hero.add_equipment(slot, item)
        
        return jsonify({
            "status": "success", 
            "hero": hero.to_dict(),
            "message": "勇者信息分析完成"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/npcs', methods=['GET'])
def get_npcs():
    """获取所有NPC信息"""
    npcs = generate_npc_info()
    
    # 将NPC对象转换为字典
    npcs_dict = {}
    for npc_id, npc in npcs.items():
        npcs_dict[npc_id] = npc.to_dict()
    
    return jsonify(npcs_dict)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
