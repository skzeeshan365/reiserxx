import re

from django import forms
from django.core.exceptions import ValidationError

from main.utils import is_valid_email


class DonationForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'placeholder': 'Full name', 'class': 'form-control', 'id': 'name'}), label=False)
    email = forms.EmailField(max_length=100,
        widget=forms.EmailInput(attrs={'placeholder': 'Email address', 'class': 'form-control', 'id': 'email'}), label=False)
    amount = forms.CharField(widget=forms.IntegerField(), label=False)
    recaptcha_response = forms.CharField(widget=forms.HiddenInput())

    def clean_email(self):
        email = self.cleaned_data['email']
        if not re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email):
            raise ValidationError('Invalid email address')
        else:
            is_valid, error = is_valid_email(email)
            if error is not None:
                raise forms.ValidationError(error)
            elif not is_valid:
                raise forms.ValidationError("Please enter a valid email address")
        return email