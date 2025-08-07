import os
import sys
import pandas as pd
import requests
import math
import threading
import time
from datetime import datetime, timedelta
# import datetime
# from blinker import signal

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, '..'))
from logger         import LoggerSingleton
from data_models    import payments_model

from payments.yookassa_api import Yookassa
from payments.base_pay_system import BasePaymentSystem
from Control.payment_info import SubscriptionPaymentInfo
import signals



# post_signal = signal('PaymentManager')

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

        self._payments: list[BasePaymentSystem] = []        # Список SubscriptionPaymentInfo
        self._lock = threading.Lock()
        self._running = False
        self._worker = None
        self._interval = 30        # секунд



    def create_invoice(self, payment_system, price_in_usd, userId, description: str)-> SubscriptionPaymentInfo:
        if not self.global_enabled :
            self._logger.add_error("{}. В данный момент оплата отключена".format(str(self.__class__.__name__)))
            return None

        
        price = self.convector.usd_to_rub(price_in_usd)
        price = self.convector.custom_round(price)

        for payment in self.payment_systems:
            if isinstance(payment, Yookassa) and payment.payment_system_name == payment_system:
                payment: Yookassa  # type: ignore
                pay_info = payment.createInvoice(userId, price, 'RUB',description)
                # datetime.time
                pay_info.diedTime = datetime.now() + timedelta(minutes=30)
                self._logger.add_info('{}. Создание платежа {} для пользователя {}, payment_id= {}'.format(str(self.__class__.__name__), payment_system, userId, pay_info.payment_id))
                return pay_info
            # elif isinstance(payment, ...) and payment.payment_system_name == payment_system:
                # payment: ...
                    # print()

        return None


    def check_status(self, pay_info:SubscriptionPaymentInfo) -> SubscriptionPaymentInfo:
        for payment in self.payment_systems:
            if isinstance(payment, Yookassa) and payment.payment_system_name == pay_info.payment_system:
                payment: Yookassa  # type: ignore
                
                payment_data = payment.getStatusInvoicePayment(pay_info.payment_id)
                # pay_info = payment.update_payment_to_SubPaymentInfo(payment_data, pay_info)
                payment.update_payment_to_SubPaymentInfo(payment_data, pay_info)

                # pay_update_info
                # if pay_info.status != payment_info.
                # pay_info = payment.createInvoice(pay_info.user_id, pay_info.amount, 'RUB',description)
                # pay_info.diedTime = datetime.now() + datetime.timedelta(min=30)
                # self._logger.add_info('{}. Создание платежа {} для пользователя {}, payment_id= {}'.format(str(self.__class__.__name__), pay_info.payment_system, userId, pay_info.payment_id))
                return pay_info
            # elif isinstance(payment, ...) and payment.payment_system_name == payment_system:


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




    def add_payment(self, payment_info: SubscriptionPaymentInfo):
        # добавим новый платёж в пул
        with self._lock:
            self._payments.append(payment_info)
        self._logger.add_info(f"Добавлен платёж user_id={payment_info.user_id}")

    def remove_payment(self, payment_info: SubscriptionPaymentInfo):
        with self._lock:
            if payment_info in self._payments:
                self._payments.remove(payment_info)
                self._logger.add_warning(f"Удалён платёж user_id={payment_info.user_id}")

    def start_auto_checker(self):
        if self._worker is None:
            self._running = True
            self._worker = threading.Thread(target=self._payment_loop, daemon=True)
            self._worker.start()
            self._logger.add_info("Таймер автопроверки запущен.")

    def stop_auto_checker(self):
        self._running = False
        if self._worker:
            self._worker.join()
        self._logger.add_warning("Таймер автопроверки остановлен.")

    def _on_payment_succeeded(self, payment_info: SubscriptionPaymentInfo):
        self._logger.add_info(f"Оплата успешна user_id={payment_info.user_id}, id={payment_info.payment_id}")
        # сигнал/коллбек на ваш вкус: GUI, email, другой компонент
        print(f"== SIGNAL paymentSucceeded: user_id={payment_info.user_id}")
        signals.finish_payment.send('PaymentManager', userId=payment_info.user_id, data=payment_info)

    def _payment_loop(self):
        while self._running:
            time.sleep(self._interval)
            now = datetime.now()
            to_remove = []
            with self._lock:
                for pay_info in self._payments:
                    # Время "смерти" истекло?
                    if pay_info.diedTime and now > pay_info.diedTime:
                        self._logger.add_warning(f"Оплата user_id={pay_info.user_id} НЕ УСПЕШНА — истекло время ожидания.")
                        print(f"Время истекло для user_id={pay_info.user_id}, платеж удалён из пула.")
                        to_remove.append(pay_info)
                        continue
                    # Успешная оплата?
                    # if payment.check_invoice():
                    pay_info = self.check_status(pay_info)

                    if pay_info.status == 'succeeded':
                        self._on_payment_succeeded(pay_info)
                        to_remove.append(pay_info)
                    elif pay_info.status == 'waiting_for_capture':
                        self._logger.add_critical('{}. Пока не определил что делать со статусом оплаты waiting_for_capture'.format(str(self.__class__.__name__)) ) ############!!!!!!!!!!!
                    elif pay_info.status == 'canceled':
                        self._payments.remove(p)

                for p in to_remove:
                    self._payments.remove(p)







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



