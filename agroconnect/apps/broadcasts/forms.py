from django import forms
from django.contrib.auth.validators import UnicodeUsernameValidator

NIGERIAN_STATES = [
    ('', '-- Select State --'),
    ('Abia', 'Abia'), ('Adamawa', 'Adamawa'), ('Akwa Ibom', 'Akwa Ibom'),
    ('Anambra', 'Anambra'), ('Bauchi', 'Bauchi'), ('Bayelsa', 'Bayelsa'),
    ('Benue', 'Benue'), ('Borno', 'Borno'), ('Cross River', 'Cross River'),
    ('Delta', 'Delta'), ('Ebonyi', 'Ebonyi'), ('Edo', 'Edo'), ('Ekiti', 'Ekiti'),
    ('Enugu', 'Enugu'), ('FCT', 'FCT - Abuja'), ('Gombe', 'Gombe'),
    ('Imo', 'Imo'), ('Jigawa', 'Jigawa'), ('Kaduna', 'Kaduna'),
    ('Kano', 'Kano'), ('Katsina', 'Katsina'), ('Kebbi', 'Kebbi'),
    ('Kogi', 'Kogi'), ('Kwara', 'Kwara'), ('Lagos', 'Lagos'),
    ('Nasarawa', 'Nasarawa'), ('Niger', 'Niger'), ('Ogun', 'Ogun'),
    ('Ondo', 'Ondo'), ('Osun', 'Osun'), ('Oyo', 'Oyo'),
    ('Plateau', 'Plateau'), ('Rivers', 'Rivers'), ('Sokoto', 'Sokoto'),
    ('Taraba', 'Taraba'), ('Yobe', 'Yobe'), ('Zamfara', 'Zamfara'),
]

UNIT_CHOICES = [
    ('kg', 'kg'), ('tonne', 'tonne'), ('bag', 'bag'),
    ('crate', 'crate'), ('litre', 'litre'), ('unit', 'unit'),
]


class BroadcastForm(forms.Form):
    broadcaster_name = forms.CharField(max_length=200, label='Your Name')
    broadcaster_phone = forms.CharField(max_length=20, label='Phone Number')
    produce_name = forms.CharField(max_length=200, label='Produce Needed')
    offered_price = forms.DecimalField(max_digits=10, decimal_places=2, min_value=1, label='Price per Unit (₦)')
    quantity_wanted = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01, label='Quantity Needed')
    unit = forms.ChoiceField(choices=UNIT_CHOICES, label='Unit')
    state = forms.ChoiceField(choices=NIGERIAN_STATES, label='Preferred State')
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label='Additional Notes')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
