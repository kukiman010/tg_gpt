import os
import sys
import uuid
import time
import hashlib
from abc import ABC, abstractmethod

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, '..'))
from logger import LoggerSingleton


class BasePaymentSystem(ABC):
    def __init__(self, logName = 'payment_system.log'):
        self._logger = LoggerSingleton.new_instance(logName)

    def generate_payment_label(self, user_id, prefix="PAY") -> str:
        timestamp = int(time.time())
        unique_id = uuid.uuid4().hex[:8]  
        
        label = f"{prefix}_{user_id}_{unique_id}_{timestamp}"
        checksum = hashlib.md5(label.encode()).hexdigest()[:4]
        
        return f"{label}_{checksum}"
    

    @abstractmethod
    def createInvoice():
        0

    @abstractmethod
    def getStatusInvoicePayment():
        0

    @abstractmethod
    def cancelInvoicePayment():
        0

    @abstractmethod
    def accesInvoicePayment():
        0

    @abstractmethod
    def class_to_paymentInfo():
        0