from django import forms
from apps.listings.models import Listing


class StoryForm(forms.Form):
    listing = forms.ModelChoiceField(
        queryset=Listing.objects.filter(is_active=True),
        required=False,
        label='Related Listing (optional)',
        empty_label='-- No listing --',
        to_field_name=None,
    )

    def clean_listing(self):
        listing = self.cleaned_data.get('listing')
        return listing  # None is fine
    title = forms.CharField(max_length=300, label='Story Title')
    body = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6}),
        label='Your Story',
        help_text='Max 500 characters. No links, phone numbers, or social handles.',
    )
    photo = forms.ImageField(required=False, label='Photo (optional)')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
