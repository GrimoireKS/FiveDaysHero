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
        return {
            "current_day": f"第{self.current_day}天",
            "current_time": self.current_time,
            "weather": self.weather,
            "locations": self.locations,
            "events": self.events
        }
    
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
        