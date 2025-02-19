from datetime import date

class TodaySingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TodaySingleton, cls).__new__(cls)
            cls._instance.today = date.today()
        return cls._instance

    def get_today(self):
        return self.today

    def set_today(self):
        self.today = date.today()