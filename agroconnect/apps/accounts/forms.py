from django import forms
from django.contrib.auth import get_user_model

Customer = get_user_model()

NIGERIAN_STATES = [
    ('', 'Select State'),
    ('Abia','Abia'),('Adamawa','Adamawa'),('Akwa Ibom','Akwa Ibom'),
    ('Anambra','Anambra'),('Bauchi','Bauchi'),('Bayelsa','Bayelsa'),
    ('Benue','Benue'),('Borno','Borno'),('Cross River','Cross River'),
    ('Delta','Delta'),('Ebonyi','Ebonyi'),('Edo','Edo'),('Ekiti','Ekiti'),
    ('Enugu','Enugu'),('FCT','FCT - Abuja'),('Gombe','Gombe'),
    ('Imo','Imo'),('Jigawa','Jigawa'),('Kaduna','Kaduna'),
    ('Kano','Kano'),('Katsina','Katsina'),('Kebbi','Kebbi'),
    ('Kogi','Kogi'),('Kwara','Kwara'),('Lagos','Lagos'),
    ('Nasarawa','Nasarawa'),('Niger','Niger'),('Ogun','Ogun'),
    ('Ondo','Ondo'),('Osun','Osun'),('Oyo','Oyo'),
    ('Plateau','Plateau'),('Rivers','Rivers'),('Sokoto','Sokoto'),
    ('Taraba','Taraba'),('Yobe','Yobe'),('Zamfara','Zamfara'),
]

W = {'class': 'form-control'}


class CustomerRegistrationForm(forms.Form):
    full_name        = forms.CharField(max_length=150, widget=forms.TextInput(attrs={**W, 'placeholder': 'Full Name'}))
    email            = forms.EmailField(widget=forms.EmailInput(attrs={**W, 'placeholder': 'Email Address'}))
    phone            = forms.CharField(max_length=20, widget=forms.TextInput(attrs={**W, 'placeholder': 'Phone Number e.g. 08012345678'}))
    state            = forms.ChoiceField(choices=NIGERIAN_STATES, widget=forms.Select(attrs=W))
    address          = forms.CharField(required=False, widget=forms.Textarea(attrs={**W, 'rows': 2, 'placeholder': 'Home / Delivery Address (optional)'}))
    password         = forms.CharField(widget=forms.PasswordInput(attrs={**W, 'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={**W, 'placeholder': 'Confirm Password'}))

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('confirm_password'):
            raise forms.ValidationError('Passwords do not match.')
        return cleaned


class LoginForm(forms.Form):
    email    = forms.EmailField(widget=forms.EmailInput(attrs={**W, 'placeholder': 'Email Address'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={**W, 'placeholder': 'Password'}))


class ProfileUpdateForm(forms.ModelForm):
    """Allow users to update profile including farmer store details."""
    class Meta:
        model  = Customer
        fields = ['first_name', 'last_name', 'phone', 'state', 'address',
                  'store_name', 'store_address']
        widgets = {
            'first_name':    forms.TextInput(attrs=W),
            'last_name':     forms.TextInput(attrs=W),
            'phone':         forms.TextInput(attrs={**W, 'placeholder': '08012345678'}),
            'state':         forms.Select(choices=NIGERIAN_STATES, attrs=W),
            'address':       forms.Textarea(attrs={**W, 'rows': 2, 'placeholder': 'Your delivery address'}),
            'store_name':    forms.TextInput(attrs={**W, 'placeholder': 'Your farm or store name'}),
            'store_address': forms.Textarea(attrs={**W, 'rows': 2, 'placeholder': 'Farm/store pickup address'}),
        }
        labels = {
            'store_name':    'Farm / Store Name (farmers only)',
            'store_address': 'Farm / Store Pickup Address (farmers only)',
        }
