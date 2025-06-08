from .common import TimeOfDay

class Event:
    """事件类，包含事件的基本信息和属性"""
    def __init__(self, time_of_day, description: str):
        # 如果time_of_day是字符串，尝试转换为TimeOfDay枚举
        if isinstance(time_of_day, str):
            try:
                self.time_of_day = TimeOfDay[time_of_day]
            except KeyError:
                # 如果找不到对应的枚举值，使用字符串
                self.time_of_day = time_of_day
        else:
            self.time_of_day = time_of_day
        self.description = description
        
    def to_dict(self):
        """将事件对象转换为字典"""
        return {
            "time_of_day": self.time_of_day.name if isinstance(self.time_of_day, TimeOfDay) else self.time_of_day,
            "description": self.description
        }
        

class EventList:
    def __init__(self):
        self.events = []

    def has_event(self, time_of_day: TimeOfDay) -> Event | None:
        return next((event for event in self.events if event.time_of_day == time_of_day), None)