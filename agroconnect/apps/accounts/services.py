import secrets
from datetime import timedelta
from django.utils import timezone
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

Customer = get_user_model()
signer = TimestampSigner()


def create_customer(full_name, email, phone, state, password):
    """Create a new customer account with hashed password."""
    if Customer.objects.filter(email=email).exists():
        from django.core.exceptions import ValidationError
        raise ValidationError('An account with this email already exists.')
    first_name, *rest = full_name.split(' ', 1)
    last_name = rest[0] if rest else ''
    customer = Customer.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        state=state,
    )
    return customer


def send_verification_email(customer):
    """Send email verification link to customer."""
    token = signer.sign(str(customer.pk))
    verification_url = f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/accounts/verify/{token}/"
    send_mail(
        subject='Verify your AgroConnect account',
        message=f'Hi {customer.first_name},\n\nClick to verify: {verification_url}\n\nThis link expires in 60 minutes.',
        from_email='noreply@agroconnect.ng',
        recipient_list=[customer.email],
        fail_silently=True,
    )


def verify_email_token(token):
    """Validate email token. Returns Customer or None."""
    try:
        pk = signer.unsign(token, max_age=3600)
        customer = Customer.objects.get(pk=pk)
        customer.email_verified = True
        customer.save(update_fields=['email_verified'])
        return customer
    except (BadSignature, SignatureExpired, Customer.DoesNotExist):
        return None


def lock_account(customer):
    """Lock account for 15 minutes after too many failures."""
    customer.is_locked = True
    customer.locked_until = timezone.now() + timedelta(minutes=15)
    customer.failed_login_attempts = 0
    customer.save(update_fields=['is_locked', 'locked_until', 'failed_login_attempts'])


def is_account_locked(customer):
    """Return True if account is currently locked."""
    if customer.is_locked and customer.locked_until:
        if timezone.now() < customer.locked_until:
            return True
        else:
            customer.is_locked = False
            customer.save(update_fields=['is_locked'])
    return False
