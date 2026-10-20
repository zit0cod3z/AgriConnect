import logging
from django.conf import settings

logger = logging.getLogger('notifications')


class SMSAdapter:
    def send(self, phone, message):
        backend = getattr(settings, 'SMS_BACKEND', 'console')
        if backend == 'africastalking':
            return self._send_africastalking(phone, message)
        elif backend == 'console':
            print(f"[SMS to {phone}]: {message}")
            return True
        return True

    def _send_africastalking(self, phone, message):
        try:
            import africastalking
            africastalking.initialize(settings.AT_USERNAME, settings.AT_API_KEY)
            sms = africastalking.SMS
            sms.send(message, [phone])
            return True
        except Exception as e:
            logger.error(f"SMS failed to {phone}: {e}")
            return False
