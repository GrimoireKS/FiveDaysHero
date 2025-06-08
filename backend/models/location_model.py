class Location:
    """地点类，包含地点的基本信息和属性"""
    def __init__(self, name:str, description:str):
        self.name = name
        self.description = description
    
    def to_dict(self):
        """将地点对象转换为字典"""
        return {
            "name": self.name,
            "description": self.description
        }
    
    def update_description(self, new_description):
        """更新地点描述"""
        self.description = new_description
