from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from .forms import CustomerRegistrationForm, LoginForm
from .services import create_customer, send_verification_email, verify_email_token, lock_account, is_account_locked
from django.core.exceptions import ValidationError

Customer = get_user_model()


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return render(request, 'accounts/register.html', {'form': CustomerRegistrationForm()})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            try:
                customer = create_customer(
                    d['full_name'], d['email'], d['phone'], d['state'], d['password']
                )
                # Save address if provided
                if d.get('address'):
                    customer.address = d['address']
                    customer.save(update_fields=['address'])
                # Try to send verification email but don't block registration if it fails
                try:
                    send_verification_email(customer)
                    messages.success(
                        request,
                        'Account created! Check your email for a verification link, '
                        'or you can log in directly and verify later.'
                    )
                except Exception:
                    messages.success(request, 'Account created! You can now log in.')

                # Auto-login immediately after registration — no email barrier
                user = authenticate(
                    request,
                    username=customer.username,
                    password=d['password'],
                )
                if user:
                    login(request, user)
                    return redirect('accounts:dashboard')
                return redirect('accounts:login')

            except ValidationError as e:
                form.add_error(None, str(e))
        return render(request, 'accounts/register.html', {'form': form})


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return render(request, 'accounts/login.html', {'form': LoginForm()})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email    = form.cleaned_data['email'].strip().lower()
            password = form.cleaned_data['password']
            try:
                user_obj = Customer.objects.get(email__iexact=email)

                if is_account_locked(user_obj):
                    messages.error(
                        request,
                        'Account locked for 15 minutes due to too many failed attempts.'
                    )
                    return render(request, 'accounts/login.html', {'form': form})

                # authenticate() needs username (which equals email for our model)
                user = authenticate(request, username=user_obj.username, password=password)

                if user is not None:
                    user_obj.failed_login_attempts = 0
                    user_obj.save(update_fields=['failed_login_attempts'])
                    login(request, user)
                    next_url = request.GET.get('next', '')
                    return redirect(next_url if next_url else 'accounts:dashboard')
                else:
                    user_obj.failed_login_attempts += 1
                    user_obj.save(update_fields=['failed_login_attempts'])
                    if user_obj.failed_login_attempts >= 5:
                        lock_account(user_obj)
                        messages.error(
                            request,
                            'Too many failed attempts. Account locked for 15 minutes.'
                        )
                    else:
                        remaining = 5 - user_obj.failed_login_attempts
                        messages.error(
                            request,
                            f'Incorrect password. {remaining} attempt{"s" if remaining != 1 else ""} remaining.'
                        )

            except Customer.DoesNotExist:
                # Generic message to avoid user enumeration
                messages.error(request, 'No account found with that email address.')

        return render(request, 'accounts/login.html', {'form': form})


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('/')

    # Also handle GET logout (e.g. clicking a link)
    def get(self, request):
        logout(request)
        return redirect('/')


class VerifyEmailView(View):
    def get(self, request, token):
        customer = verify_email_token(token)
        if customer:
            messages.success(request, 'Email verified! You can now log in.')
        else:
            messages.error(request, 'Verification link is invalid or has expired.')
        return redirect('accounts:login')


class DashboardView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=/accounts/dashboard/')
        from apps.orders.models import Order
        from apps.negotiations.models import Offer
        from apps.notifications.models import Notification
        from apps.notifications.services import get_unread_count
        recent_orders = Order.objects.filter(
            customer=request.user
        ).order_by('-created_at')[:5]
        recent_notifications = Notification.objects.filter(
            customer=request.user
        ).order_by('-created_at')[:5]
        unread_count = get_unread_count(request.user)
        stats = {
            'active_listings': request.user.listings.filter(is_active=True).count(),
            'pending_offers': Offer.objects.filter(
                customer=request.user, status='pending'
            ).count(),
            'active_orders': Order.objects.filter(
                customer=request.user
            ).exclude(status__in=['delivered', 'cancelled', 'closed']).count(),
            'farmer_pending_orders': Order.objects.filter(
                farmer_phone=request.user.phone,
                status='pending_confirmation'
            ).count() if request.user.phone else 0,
        }
        return render(request, 'accounts/dashboard.html', {
            'recent_orders': recent_orders,
            'recent_notifications': recent_notifications,
            'unread_count': unread_count,
            'stats': stats,
        })


class PasswordResetView(View):
    def get(self, request):
        return render(request, 'accounts/password_reset.html')

    def post(self, request):
        email = request.POST.get('email', '').strip().lower()
        try:
            customer = Customer.objects.get(email__iexact=email)
            try:
                send_verification_email(customer)
            except Exception:
                pass
            messages.success(request, 'If that email exists, a reset link has been sent.')
        except Customer.DoesNotExist:
            messages.success(request, 'If that email exists, a reset link has been sent.')
        return redirect('accounts:login')


from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password


class DebugAuthView(View):
    """Temporary debug view — shows admin user status on Render. Remove after fixing."""
    def get(self, request):
        Customer = get_user_model()
        email = 'admin@agroconnect.ng'
        password = 'Admin@2026'

        user = Customer.objects.filter(email=email).first()
        if not user:
            all_users = list(Customer.objects.values('pk', 'username', 'email', 'is_staff', 'is_superuser', 'is_active'))
            return JsonResponse({'error': 'admin user not found', 'all_users': all_users})

        auth_result = authenticate(request, username=user.username, password=password)
        pw_check = check_password(password, user.password)

        from django.conf import settings
        return JsonResponse({
            'user_found': True,
            'pk': user.pk,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'is_active': user.is_active,
            'has_usable_password': user.has_usable_password(),
            'password_check': pw_check,
            'authenticate_ok': auth_result is not None,
            'auth_backends': settings.AUTHENTICATION_BACKENDS,
            'total_users': Customer.objects.count(),
        })


class ProfileUpdateView(LoginRequiredMixin, View):
    def get(self, request):
        from .forms import ProfileUpdateForm
        form = ProfileUpdateForm(instance=request.user)
        return render(request, 'accounts/profile.html', {'form': form})

    def post(self, request):
        from .forms import ProfileUpdateForm
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        return render(request, 'accounts/profile.html', {'form': form})
