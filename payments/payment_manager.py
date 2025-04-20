import os
import sys
import pandas as pd
import requests
import math

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, '..'))
from logger         import LoggerSingleton
from data_models    import payments_model
from Payments.yookassa_api import Yookassa
from Payments.base_pay_system import BasePaymentSystem
from Control.payment_info import SubscriptionPaymentInfo




class PaymentManager:
    def __init__(self, is_work):
        self._logger = LoggerSingleton.new_instance('logs/payment_system.log')

        self.active_services = {}
        self.global_enabled = is_work
        self.buttons = {}
        self.payment_system_and_code_buttons = {}
        self.convector = OnlineConvector()
        self.payment_systems : list[BasePaymentSystem] = []
        
        self.payment_systems.append(Yookassa())



    def create_invoice(self, payment_system, price_in_usd, userId, description: str)-> SubscriptionPaymentInfo:
        if not self.global_enabled :
            self._logger.add_error("{}. В данный момент оплата отключена".format(str(self.__class__.__name__)))
            return None

        for payment in self.payment_systems:
            price = self.convector.usd_to_rub(price_in_usd)
            price = self.convector.custom_round(price)

        if isinstance(payment, Yookassa) and payment.payment_system_name == payment_system:
            payment: Yookassa  # type: ignore
            pay_info = payment.createInvoice(userId, price, 'RUB',description)
            self._logger.add_info('{}. Создание платежа {} для пользователя {}, payment_id= {}'.format(str(self.__class__.__name__), payment_system, userId, pay_info.payment_id))
            return pay_info
            # print()
        # elif isinstance(payment, ...) and payment.payment_system_name == payment_system:
            # payment: ...
                # print()

        return None


    # def check_status(self, pay_info:SubscriptionPaymentInfo) -> SubscriptionPaymentInfo:


    def get_buttons(self) -> dict[payments_model]:
        return self.buttons

    def stop_payments(self):
        self.global_enabled = False

    def resume_payments(self):
        self.global_enabled = True


    def update(self, list_payment : dict[payments_model]):
        if list_payment:
            self.active_services.clear()
            self.active_services = list_payment.copy()
            list_payment.clear()
            
            self.buttons.clear()
            self.payment_system_and_code_buttons.clear()

            for system in self.active_services:
                if system.is_enabled:
                    button_name = 'set_payments_' + system.name
                    self.buttons[button_name] = system.description
                    self.payment_system_and_code_buttons[system.name] = button_name

        else:
            self._logger.add_error("{}. Не удалось обновить список сервисов".format(str(self.__class__.__name__)))







class OnlineConvector:
    def get_fiat_rate(self, ticker: str) -> float:
        try:
            url = "https://www.fontanka.ru/currency.html"
            df = pd.read_html(url)[0]
            rate = df.loc[df['Валюта'].str.lower() == ticker.lower(), 'Курс'].values
            if rate.size == 0:
                raise ValueError(f"Валюта {ticker} не найдена.")
            rate_value = rate[0]
            if isinstance(rate_value, str):
                rate_value = rate_value.replace(',', '.')
            return float(rate_value)
        except Exception as e:
            print(f"Ошибка при получении курса {ticker}: {e}")
            return None 

    def get_crypto_to_fiat(self, crypto: str, fiat: str) -> float:
        url = f'https://api.coingecko.com/api/v3/simple/price?ids={crypto.lower()}&vs_currencies={fiat.lower()}'
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            price = data.get(crypto.lower(), {}).get(fiat.lower())
            if price is None:
                raise ValueError(f"{crypto.upper()} to {fiat.upper()} не найден в API.")
            return float(price)
        except Exception as e:
            print(f"Ошибка при получении курса {crypto.upper()} к {fiat.upper()}: {e}")
            return None

    def usd_to_rub(self, amount: float) -> float:
        rate = self.get_fiat_rate('usd')
        if rate is not None:
            return amount * rate
        return None

    def usd_to_bit(self, amount: float) -> float:
        btc_price = self.get_crypto_to_fiat('bitcoin', 'usd')
        if btc_price:
            return amount / btc_price
        return None

    def usd_to_usdt(self, amount: float) -> float:
        return amount

    def get_btc_to_usd(self) -> float:
        return self.get_crypto_to_fiat('bitcoin', 'usd')

    def get_btc_to_rub(self) -> float:
        return self.get_crypto_to_fiat('bitcoin', 'rub')

    def get_fiat_usd(self) -> float:
        return self.get_fiat_rate('usd')
    
    def get_fiat_eur(self) -> float:
        return self.get_fiat_rate('eur')
    
    def custom_round(self, amount):
        """
        Округляет крипту к следующему значимому цифро-месту после запятой,
        а для фиата — до ближайшего большего целого или десятка.
        """
        # Крипта: малое число (<1), округляем до первой значимой цифры после не-нуля
        if abs(amount) < 1:
            # Определить позицию первой значимой цифры после 0.
            str_v = '{:.12f}'.format(amount).rstrip('0')
            dot = str_v.find('.')
            first_nonzero = next((i for i, c in enumerate(str_v[dot+1:], start=dot+1) if c not in '0.'), None)
            # Округляем к следующей цифре после первой значимой
            if first_nonzero is not None:
                precision = first_nonzero - dot + 1  # +1 чтобы оставить следующее не-0
            else:
                precision = 6  # fallback
            factor = 10 ** precision
            return math.ceil(amount * factor) / factor

        # Фиат: если больше 100 — округлять вверх к следующему десятку
        elif amount >= 100:
            return math.ceil(amount / 10) * 10
        # Если меньше 100, округлять до целого
        else:
            return math.ceil(amount)



