"""
游戏模型类定义
包含 World、Hero 和 NPC 类
"""

class World:
    """世界类，包含游戏世界的基本信息"""
    
    def __init__(self, current_day=1, current_time="上午", weather="晴天"):
        """
        初始化世界对象
        
        参数:
            current_day (int): 当前游戏天数
            current_time (str): 当前游戏时间
            weather (str): 当前天气状况
        """
        self.current_day = current_day
        self.current_time = current_time
        self.weather = weather
        self.locations = {}  # 世界中的地点
        self.events = []     # 世界事件列表
        
    def to_dict(self):
        """将世界对象转换为字典"""
        result = {
            "current_day": f"第{self.current_day}天",
            "current_time": self.current_time,
            "weather": self.weather,
            "locations": self.locations,
            "events": self.events
        }

        # 如果有世界描述信息，添加到返回结果中
        if hasattr(self, 'world_info'):
            result.update(self.world_info)

        return result
    
    def update_weather(self, new_weather):
        """更新天气状况"""
        self.weather = new_weather
        
    def add_location(self, location_id, location_data):
        """添加地点"""
        self.locations[location_id] = location_data
        
    def add_event(self, event):
        """添加世界事件"""
        self.events.append(event)


class Hero:
    """勇者类，包含勇者的基本信息和属性"""
    
    def __init__(self, name="无名勇者", gender="未知", profession="勇者", age=18):
        """
        初始化勇者对象
        
        参数:
            name (str): 勇者姓名
            gender (str): 勇者性别
            profession (str): 勇者职业
            age (int): 勇者年龄
        """
        self.basic_info = {
            "name": name,
            "gender": gender,
            "profession": profession,
            "age": age,
            "personality": ""
        }
        
        self.stats = {
            "hp": 100,
            "mp": 100,
            "strength": 5,
            "intelligence": 5,
            "agility": 5,
            "luck": 5
        }
        
        self.equipment = {}
        self.inventory = []
        self.events = []
        
    def to_dict(self):
        """将勇者对象转换为字典"""
        return {
            "basic_info": self.basic_info,
            "stats": self.stats,
            "equipment": self.equipment,
            "inventory": self.inventory,
            "events": self.events
        }
    
    def update_stats(self, stat_name, value):
        """更新勇者属性"""
        if stat_name in self.stats:
            self.stats[stat_name] = value
            
    def add_equipment(self, slot, item):
        """添加装备"""
        self.equipment[slot] = item
        
    def add_to_inventory(self, item):
        """添加物品到背包"""
        self.inventory.append(item)
        
    def remove_from_inventory(self, item):
        """从背包中移除物品"""
        if item in self.inventory:
            self.inventory.remove(item)


class NPC:
    """NPC类，包含NPC的基本信息和属性"""
    
    def __init__(self, name, age, gender, profession):
        """
        初始化NPC对象
        
        参数:
            name (str): NPC姓名
            age (int): NPC年龄
            gender (str): NPC性别
            profession (str): NPC职业
        """
        self.name = name
        self.age = age
        self.gender = gender
        self.profession = profession

        self.events = []
        
        self.stats = {
            "strength": 0,
            "intelligence": 0,
            "agility": 0,
            "luck": 0
        }
        
        self.relationship = 0  # 与勇者的关系值，0为中立

    def init_from_json(self, json_data):
        self.name = json_data["name"]
        self.age = json_data["age"]
        self.gender = json_data["gender"]
        self.profession = json_data["profession"]
        self.stats = json_data["stats"]
        self.relationship = json_data["relationship"]
        for event in json_data["events"]:
            self.events.append(Event(event["time_of_day"], event["description"]))

    def to_dict(self):
        """将NPC对象转换为字典"""
        events_dict = [event.to_dict() for event in self.events] if hasattr(self, 'events') else []
        return {
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "profession": self.profession,
            "stats": self.stats,
            "relationship": self.relationship,
            "events": events_dict
        }
    
    def update_stats(self, stat_name, value):
        """更新NPC属性"""
        if stat_name in self.stats:
            self.stats[stat_name] = value
            
    def update_relationship(self, value):
        """更新与勇者的关系值"""
        self.relationship = value


class RelationshipGraph:
    """人物关系图类，用于记录和管理角色之间的关系"""

    def __init__(self):
        """
        初始化关系图对象
        使用有向图结构存储关系，支持A对B和B对A的关系不同
        """
        self.relationships = {}  # 存储关系的有向图 {角色A: {角色B: 关系值}}

    def set_relationship(self, character_a, character_b, relationship_value):
        """
        设置角色A对角色B的关系

        参数:
            character_a (str): 角色A的名称
            character_b (str): 角色B的名称
            relationship_value (int|str): 关系值，可以是数值(如好感度)或字符串描述
        """
        if character_a not in self.relationships:
            self.relationships[character_a] = {}

        self.relationships[character_a][character_b] = relationship_value

    def get_relationship(self, character_a, character_b):
        """
        获取角色A对角色B的关系

        参数:
            character_a (str): 角色A的名称
            character_b (str): 角色B的名称

        返回:
            int|str|None: 关系值，如果没有设置关系则返回None
        """
        if character_a in self.relationships:
            return self.relationships[character_a].get(character_b, None)
        return None

    def get_all_relationships_for_character(self, character):
        """
        获取某个角色对所有其他角色的关系

        参数:
            character (str): 角色名称

        返回:
            dict: {角色名: 关系值} 的字典，如果角色不存在则返回空字典
        """
        return self.relationships.get(character, {}).copy()

    def get_mutual_relationship(self, character_a, character_b):
        """
        获取两个角色之间的双向关系

        参数:
            character_a (str): 角色A的名称
            character_b (str): 角色B的名称

        返回:
            dict: {"a_to_b": 关系值, "b_to_a": 关系值}
        """
        return {
            "a_to_b": self.get_relationship(character_a, character_b),
            "b_to_a": self.get_relationship(character_b, character_a)
        }

    def remove_relationship(self, character_a, character_b):
        """
        移除角色A对角色B的关系

        参数:
            character_a (str): 角色A的名称
            character_b (str): 角色B的名称
        """
        if character_a in self.relationships and character_b in self.relationships[character_a]:
            del self.relationships[character_a][character_b]

            # 如果角色A没有其他关系了，移除该角色的条目
            if not self.relationships[character_a]:
                del self.relationships[character_a]

    def get_all_characters(self):
        """
        获取关系图中涉及的所有角色名称

        返回:
            set: 所有角色名称的集合
        """
        characters = set(self.relationships.keys())
        for relations in self.relationships.values():
            characters.update(relations.keys())
        return characters

    def to_dict(self):
        """将关系图对象转换为字典"""
        return {
            "relationships": self.relationships.copy()
        }

    def from_dict(self, data):
        """从字典数据恢复关系图对象"""
        if "relationships" in data:
            self.relationships = data["relationships"].copy()

    def __str__(self):
        """返回关系图的字符串表示"""
        if not self.relationships:
            return "关系图为空"

        result = "人物关系图:\n"
        for character_a, relations in self.relationships.items():
            for character_b, relationship in relations.items():
                result += f"  {character_a} -> {character_b}: {relationship}\n"
        return result
        