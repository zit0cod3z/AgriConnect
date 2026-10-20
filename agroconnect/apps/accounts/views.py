from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
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
                customer = create_customer(d['full_name'], d['email'], d['phone'], d['state'], d['password'])
                send_verification_email(customer)
                messages.success(request, 'Account created! Check your email to verify your account.')
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
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user_obj = Customer.objects.get(email=email)
                if is_account_locked(user_obj):
                    messages.error(request, 'Account locked for 15 minutes due to too many failed attempts.')
                    return render(request, 'accounts/login.html', {'form': form})
                user = authenticate(request, username=email, password=password)
                if user:
                    user_obj.failed_login_attempts = 0
                    user_obj.save(update_fields=['failed_login_attempts'])
                    login(request, user)
                    return redirect(request.GET.get('next', 'accounts:dashboard'))
                else:
                    user_obj.failed_login_attempts += 1
                    user_obj.save(update_fields=['failed_login_attempts'])
                    if user_obj.failed_login_attempts >= 5:
                        lock_account(user_obj)
                        messages.error(request, 'Too many failed attempts. Account locked for 15 minutes.')
                    else:
                        messages.error(request, f'Invalid credentials. {5 - user_obj.failed_login_attempts} attempts left.')
            except Customer.DoesNotExist:
                messages.error(request, 'Invalid email or password.')
        return render(request, 'accounts/login.html', {'form': form})


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('/')


class VerifyEmailView(View):
    def get(self, request, token):
        customer = verify_email_token(token)
        if customer:
            messages.success(request, 'Email verified! You can now log in.')
        else:
            messages.error(request, 'Verification link is invalid or expired.')
        return redirect('accounts:login')


class DashboardView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect(f'/accounts/login/?next=/accounts/dashboard/')
        from apps.orders.models import Order
        from apps.negotiations.models import Offer
        from apps.notifications.models import Notification
        from apps.notifications.services import get_unread_count
        recent_orders = Order.objects.filter(customer=request.user).order_by('-created_at')[:5]
        recent_notifications = Notification.objects.filter(customer=request.user).order_by('-created_at')[:5]
        unread_count = get_unread_count(request.user)
        stats = {
            'active_listings': request.user.listings.filter(is_active=True).count(),
            'pending_offers': Offer.objects.filter(customer=request.user, status='pending').count(),
            'active_orders': Order.objects.filter(customer=request.user).exclude(status__in=['delivered','cancelled','closed']).count(),
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
        email = request.POST.get('email', '')
        try:
            customer = Customer.objects.get(email=email)
            send_verification_email(customer)
            messages.success(request, 'Password reset link sent to your email.')
        except Customer.DoesNotExist:
            messages.info(request, 'If that email exists, a reset link has been sent.')
        return redirect('accounts:login')
