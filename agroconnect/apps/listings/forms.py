from django import forms
from .models import CATEGORY_CHOICES

NIGERIAN_STATES = [
    ('', 'Select State'), ('Abia', 'Abia'), ('Adamawa', 'Adamawa'), ('Akwa Ibom', 'Akwa Ibom'),
    ('Anambra', 'Anambra'), ('Bauchi', 'Bauchi'), ('Bayelsa', 'Bayelsa'), ('Benue', 'Benue'),
    ('Borno', 'Borno'), ('Cross River', 'Cross River'), ('Delta', 'Delta'), ('Ebonyi', 'Ebonyi'),
    ('Edo', 'Edo'), ('Ekiti', 'Ekiti'), ('Enugu', 'Enugu'), ('FCT', 'FCT - Abuja'),
    ('Gombe', 'Gombe'), ('Imo', 'Imo'), ('Jigawa', 'Jigawa'), ('Kaduna', 'Kaduna'),
    ('Kano', 'Kano'), ('Katsina', 'Katsina'), ('Kebbi', 'Kebbi'), ('Kogi', 'Kogi'),
    ('Kwara', 'Kwara'), ('Lagos', 'Lagos'), ('Nasarawa', 'Nasarawa'), ('Niger', 'Niger'),
    ('Ogun', 'Ogun'), ('Ondo', 'Ondo'), ('Osun', 'Osun'), ('Oyo', 'Oyo'),
    ('Plateau', 'Plateau'), ('Rivers', 'Rivers'), ('Sokoto', 'Sokoto'), ('Taraba', 'Taraba'),
    ('Yobe', 'Yobe'), ('Zamfara', 'Zamfara'),
]

W = {'class': 'form-control'}


class ListingForm(forms.Form):
    produce_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={**W, 'placeholder': 'e.g. Tomatoes, Rice, Garri'}))
    category = forms.ChoiceField(choices=[('', 'Select Category')] + CATEGORY_CHOICES, widget=forms.Select(attrs=W))
    quantity = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={**W, 'placeholder': 'e.g. 500'}))
    unit = forms.CharField(max_length=30, widget=forms.TextInput(attrs={**W, 'placeholder': 'e.g. kg, bags, crates'}))
    price_per_unit = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={**W, 'placeholder': 'Price in Naira'}))
    farm_state = forms.ChoiceField(choices=NIGERIAN_STATES, widget=forms.Select(attrs=W))
    farm_lga = forms.CharField(max_length=100, widget=forms.TextInput(attrs={**W, 'placeholder': 'Local Government Area'}))
    contact_phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={**W, 'placeholder': '08012345678'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={**W, 'rows': 4, 'placeholder': 'Describe your produce, farm, harvest date...'}))
    group_buy_eligible = forms.BooleanField(required=False)
    group_buy_threshold_qty = forms.DecimalField(required=False, max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs=W))
    group_buy_bulk_price = forms.DecimalField(required=False, max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs=W))


class GuestAccessForm(forms.Form):
    reference_code = forms.CharField(max_length=19, widget=forms.TextInput(attrs={**W, 'placeholder': 'XXXX-XXXX-XXXX-XXXX'}))
    contact_phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={**W, 'placeholder': '08012345678'}))
