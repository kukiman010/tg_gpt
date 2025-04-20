# https://github.com/yoomoney/yookassa-sdk-python/tree/master/docs/examples
# https://yookassa.ru/developers/payment-acceptance/testing-and-going-live/testing#test-bank-card

from yookassa import Configuration, Payment

import os, sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, '../'))
from Control.payment_info import SubscriptionPaymentInfo
from Payments.base_pay_system import BasePaymentSystem



class Yookassa(BasePaymentSystem):
    def __init__(self, botName="https://t.me/kukimanGptBot", capture = True):
        super().__init__('logs/payment_system.log')

        with open('conf/yoomoney_clientId.key', 'r', encoding="utf-8") as file:
            Configuration.account_id = file.read()

        with open('conf/yoomoney_token.key', 'r', encoding="utf-8") as file:
            Configuration.secret_key = file.read()

        self.redirect_uri = botName
        self.capture = capture
        self.payment_system_name = 'Yoomoney'

        

    def createInvoice(self, userId, sum, money_code, description) -> SubscriptionPaymentInfo:
        if not userId:
            self._logger.add_critical('Source: {}. нельзя передавать пустой userId!'.format(str(self.__class__.__name__)))
            return None
        
        label_pay = self.generate_payment_label(userId)

        if not label_pay:
            self._logger.add_critical('Source: {}. нельзя передавать пустой label_pay!'.format(str(self.__class__.__name__)))
            return None
        
        if money_code != 'RUB' or money_code != 'USD':
            money_code = 'RUB'


        try:
            payment = Payment.create(
                {
                    "amount": {
                        "value": sum,
                        "currency": money_code
                    },
                    "confirmation": {
                        "type": "redirect",
                        "return_url": self.redirect_uri
                    },
                    "capture": self.capture,
                    "description": description,
                    "metadata": {
                        "user_id": userId,
                        "payment_label": label_pay
                        # 'orderNumber': '72'
                    }

                    # "receipt": {
                    #     "customer": {
                    #         "full_name": "Ivanov Ivan Ivanovich",
                    #         "email": "email@email.ru",
                    #         "phone": "79211234567",
                    #         "inn": "6321341814"
                    #     },
                    #     "items": [
                    #         {
                    #             "description": "Переносное зарядное устройство Хувей",
                    #             "quantity": "1.00",
                    #             "amount": {
                    #                 "value": 1000,
                    #                 "currency": "RUB"
                    #             },
                    #             "vat_code": "2",
                    #             "payment_mode": "full_payment",
                    #             "payment_subject": "commodity",
                    #             "country_of_origin_code": "CN",
                    #             "product_code": "44 4D 01 00 21 FA 41 00 23 05 41 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 12 00 AB 00",
                    #             "customs_declaration_number": "10714040/140917/0090376",
                    #             "excise": "20.00",
                    #             "supplier": {
                    #                 "name": "string",
                    #                 "phone": "string",
                    #                 "inn": "string"
                    #             }
                    #         },
                    #     ]
                    # }
                }
            )
        except Exception as e:
            self._logger.add_critical(f"{str(self.__class__.__name__)}. Ошибка: {str(e)}")
            return None

        return self.class_to_paymentInfo(payment)
    

    def getStatusInvoicePayment(self, payment_id) -> Payment:
        if not payment_id:
            self._logger.add_error('{}. Не получилось запросить статус платежа для {}: payment_id - пустой'.format(str(self.__class__.__name__), payment_id))
        try:
            payment = Payment.find_one(payment_id)
        except Exception as e:
            self._logger.add_critical(f"{str(self.__class__.__name__)}. Ошибка: {str(e)}")
            return None

        return payment


    def cancelInvoicePayment(self, payment_id) -> Payment:
        # используется тогда, когда в платеже был указан capture = false
        try: 
            payment = self.getStatusInvoicePayment(payment_id)
        except Exception as e:
            self._logger.add_critical(f"{str(self.__class__.__name__)}. Ошибка: {str(e)}")
            return None

        if payment.status == 'waiting_for_capture':
            try: 
                answer = Payment.cancel(payment_id)
            except Exception as e:
                self._logger.add_critical(f"{str(self.__class__.__name__)}. Не получилось отменить платеж. Ошибка: {str(e)}")
                return None
        
        return answer 
    
    
    def accesInvoicePayment(self, payment_id) -> Payment:
        # используется тогда, когда в платеже был указан capture = false
        try: 
            payment = self.getStatusInvoicePayment(payment_id)
        except Exception as e:
            self._logger.add_critical(f"{str(self.__class__.__name__)}. Ошибка: {str(e)}")
            return None

        if payment.status == 'waiting_for_capture':
            try: 
                answer = Payment.capture(payment_id)
            except Exception as e:
                self._logger.add_critical(f"{str(self.__class__.__name__)}. Не получилось отменить платеж. Ошибка: {str(e)}")
                return None
        else:
            return None
        
        return answer 
    

    def class_to_paymentInfo(self, payment: Payment) -> SubscriptionPaymentInfo:
        if payment :
            try:
                info = SubscriptionPaymentInfo()

                info.user_id =      payment.metadata.get('user_id')
                info.payment_id =   payment.id
                info.label_pay =    payment.metadata.get('payment_label')
                info.status =       payment.status
                info.currency =     payment.amount.currency
                info.amount =       float(payment.amount.value)
                info.payment_system = self.payment_system_name
                info.created_at =   payment.created_at
                info.description =  payment.description
                info.url_pay =      payment.confirmation.confirmation_url
                info.is_test =      payment.test

                return info

            except Exception as e:
                self._logger.add_critical(f"{str(self.__class__.__name__)}. Ошибка: {str(e)}")
                return None

        else:
            self._logger.add_error('{}. Ошибка: класс Payment - не валидный'.format(str(self.__class__.__name__)))
            return None
        
        

# userId= 111777
# # payment_id = '2f95bad0-000f-5001-8000-1d66ef30b712'


# yoo = Yookassa()

# payInfo = yoo.createInvoice(userId, 1000, "RUB", "Тест")
# print(f"Ссылка для оплаты: {payInfo.url_pay}")
# payment_id = payInfo.payment_id
# print(payment_id)

# answer = yoo.getStatusInvoicePayment(payment_id)
# # answer = yoo.cancelInvoicePayment(payment_id)
# # answer = yoo.accesInvoicePayment(payment_id)

# yoo.class_to_paymentInfo(answer)
