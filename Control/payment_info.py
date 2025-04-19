from datetime import datetime

class SubscriptionPaymentInfo:
    def __init__(self):
        self.user_id = 0                # id пользователя
        self.user_name = ''             # 
        self.payment_id = ''            #
        self.label_pay = ''             #
        self.status = ''                # например: pending/paid/failed/canceled/refunded
        self.currency = ''              # например: 'RUB', 'USD'
        self.amount = 0.0               # прайс
        self.payment_system = ''        # напр. 'Qiwi', 'Yookassa', 'SBP'
        self.created_at = datetime      #
        self.expires_at = datetime      #
        self.card_type = ''             # напр. 'Visa', 'Mastercard', 'МИР'
        self.card_number = ''           # только часть или по правилам PCI DSS
        self.email = ''                 #
        self.description = ''           #
        # self.is_recurring = False       #
        self.attempts = 0               # кол-во попыток оплаты, для аналитики
        self.updated_at = datetime      # последние изменение
        self.failure_reason = ''        # причины неуспеха
        self.provider_response = ''     # ответ платёжного шлюза
        self.metadata = dict            #
        self.url_pay = ''
        self.is_test = False            # для тестирования оплаты



    def __str__(self):
        return (f"SubscriptionPaymentInfo(user_id={self.user_id}, payment_id={self.payment_id}, amount={self.amount}, "
                f"currency={self.currency}, status={self.status}, created_at={self.created_at}, payment_system={self.payment_system})")

    def mark_paid(self):
        self.status = "paid"
        self.updated_at = datetime.now()

    def mark_failed(self, reason=""):
        self.status = "failed"
        self.failure_reason = reason
        self.updated_at = datetime.now()
        self.attempts += 1

    def add_metadata(self, key, value):
        self.metadata[key] = value
        self.updated_at = datetime.now()
