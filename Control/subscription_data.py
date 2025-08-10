import datetime

class SubscriptionData:
    def __init__(self):
        self.userId = 0
        self.tarif = 0
        self.active_until = datetime
        self.last_label = ''
        self.id = 0

    def set_userId(self,data):
        self.userId = data

    def set_tarif(self,data):
        self.tarif = data

    def set_active_until(self,data):
        self.active_until = data

    def set_last_label(self,data):
        self.last_label = data

    def set_id(self,data):
        self.id = data