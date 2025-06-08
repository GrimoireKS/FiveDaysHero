from .common import TimeOfDay
from .event_models import Event

class History:
    """记录游戏发生的历史"""
    def __init__(self):
        self.history = []

    def add_event(self, time_of_day: TimeOfDay, description: str):
        self.history.append(Event(time_of_day, description))

    def get_history(self):
        return self.history
