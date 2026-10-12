import datetime


class PaymentService:
    def __init__(self, db, env, locale, logger):
        self._db = db
        self._env = env
        self._locale = locale
        self._logger = logger

    def process_success(self, user, payment_id, amount, currency, label, payment_system="TelegramStarsPay"):
        tariff_id = self._db.get_tarif_by_paylabel(label)
        tariff = self._find_tariff(tariff_id)
        if tariff is None:
            return {
                "ok": False,
                "error": self._locale.find_translation(user.get_language(), "TR_TARRIF_DONT_LOAD").format(self._env.get_support_chat()),
            }

        fee = 0
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
        user_id = user.get_userId()
        have_sub, _hours = self._db.its_have_this_subscribe(user_id, tariff_id, now)
        tariff_hours = tariff.activity_day * 24

        self._db.update_invoice_journal(payment_id, label, "succeeded", "stars", None, fee, now)
        self._db.add_successful_payments(user_id, label, tariff_id, float(amount - fee), currency, payment_system, "stars", "", now)
        if have_sub:
            self._db.update_subscribe_date(user_id, tariff_id, tariff_hours, label)
        else:
            self._db.upsert_subscription_user(user_id, user.get_login(), tariff_id, "", tariff_hours, label)

        status_updated = False
        if int(tariff_id) == 1:
            self._db.update_status_in_users(user_id, 3)
            status_updated = True

        return {"ok": True, "tariff_id": tariff_id, "status_updated": status_updated}

    def process_finished_payment_signal(self, user_id, data, get_user_fn):
        tariff = self._find_tariff(data.tarrif)
        if tariff is None:
            return {"ok": False, "error": "tariff_not_found"}

        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
        tariff_hours = tariff.activity_day * 24
        have_sub, _hours = self._db.its_have_this_subscribe(user_id, data.tarrif, now)

        self._db.update_invoice_journal(data.payment_id, data.label_pay, data.status, data.card_type, data.card_number, data.fee, data.expires_at)
        self._db.add_successful_payments(data.user_id, data.payment_id, data.tarrif, float(data.amount - data.fee), data.currency, data.payment_system, data.card_type, data.email, data.expires_at)

        if have_sub:
            self._db.update_subscribe_date(data.user_id, data.tarrif, tariff_hours, data.payment_id)
        else:
            self._db.upsert_subscription_user(data.user_id, data.user_name, data.tarrif, data.email, tariff_hours, data.payment_id)

        user = get_user_fn(user_id)
        if int(data.tarrif) == 1:
            self._db.update_status_in_users(user_id, 3)
            return {"ok": True, "notify_lang": user.get_language() if user else "en"}
        return {"ok": True, "notify_lang": user.get_language() if user else "en"}

    def _find_tariff(self, tariff_id):
        tariffs = self._db.get_tariffs(tariff_id)
        for node in tariffs:
            if node.tariff_id == int(tariff_id):
                return node
        return None

