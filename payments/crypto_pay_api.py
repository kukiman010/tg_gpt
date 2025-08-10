# https://help.send.tg/en/articles/10279948-crypto-pay-api
# https://pypi.org/project/aiosend/
# https://github.com/layerqa/aiocryptopay

from base_pay_system import BasePaymentSystem


class Crypto_pay(BasePaymentSystem):
    def __init__(self, botName="https://t.me/kukimanGptBot", capture = True):
        super().__init__('logs/payment_system.log')