import re

import requests
from captcha.fields import ReCaptchaField
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator

from djangoProject1 import settings
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'content']

    name = forms.CharField(max_length=100, required=True, label='Your name')
    email = forms.CharField(max_length=100, required=True, label='Your email')
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), max_length=500)

    def clean_email(self):
        email = self.cleaned_data['email']
        if not re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email):
            raise ValidationError('Invalid email address')
        return email


class ContactForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'placeholder': 'Full name', 'class': 'form-control', 'id': 'name'}), label=False)
    email = forms.EmailField(max_length=100,
        widget=forms.EmailInput(attrs={'placeholder': 'Email address', 'class': 'form-control', 'id': 'email'}), label=False)
    message = forms.CharField(max_length=1500, widget=forms.Textarea(
        attrs={'placeholder': 'Message', 'class': 'form-control', 'id': 'message', 'rows': 5}), label=False, validators=[MaxLengthValidator(1500)])
    recaptcha_response = forms.CharField(widget=forms.HiddenInput())

    def clean_email(self):
        email = self.cleaned_data['email']
        if not re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email):
            raise ValidationError('Invalid email address')
        return email