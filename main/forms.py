import re

from django import forms
from django.core.exceptions import ValidationError

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
