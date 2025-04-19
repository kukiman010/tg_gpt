from yookassa_api import Yookassa


userId= 111777
payment_id = '2f95bad0-000f-5001-8000-1d66ef30b712'


yoo = Yookassa()

payInfo = yoo.createInvoice(userId, 1000, "RUB", "Тест")
print(f"Ссылка для оплаты: {payInfo.url_pay}")
payment_id = payInfo.payment_id
print(payment_id)

payment = yoo.getStatusInvoicePayment(payment_id)
# answer = yoo.cancelInvoicePayment(payment_id)
# answer = yoo.accesInvoicePayment(payment_id)

# yoo.class_to_paymentInfo(answer)

print()








