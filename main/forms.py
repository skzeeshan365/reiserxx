import re

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.urls import reverse
from sendgrid import Mail, Content, SendGridAPIClient

from djangoProject1 import settings
from .models import Comment, Subscriber
from .utils import is_valid_email


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
        else:
            is_valid, error = is_valid_email(email)
            if error is not None:
                raise forms.ValidationError(error, "ghfghfh")
            elif not is_valid:
                raise forms.ValidationError("Please enter a valid email address")
        return email


class SubscriberForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'required': True,
        }), label=False
    )
    recaptcha_response = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Subscriber
        fields = ('email',)

    def is_new_email(self):
        email = self.cleaned_data['email']
        try:
            Subscriber.objects.get(email=email)
        except Subscriber.DoesNotExist:
            return True
        return False

    def clean_email(self):
        email = self.cleaned_data['email']
        subscriber = Subscriber.objects.filter(email=email).exists()
        print(subscriber)
        if subscriber:
            raise forms.ValidationError(
                "Looks like you're already on our VIP list! Time to sit back, relax and enjoy the exclusive perks "
                "of being one of our favorites")
        else:
            # validate the email using Verifalia API
            is_valid, error = is_valid_email(email)
            if error is not None:
                raise forms.ValidationError(error)
            elif not is_valid:
                raise forms.ValidationError("Please enter a valid email address")
            return email

    def save(self, commit=True):
        subscriber = super().save(commit=False)
        if commit:
            subscriber.email = self.cleaned_data['email']
            subscriber.save()
            verification_link = self.get_verification_link(subscriber)
            self.send_verification_email(subscriber, verification_link)
        return subscriber

    def get_verification_link(self, subscriber):
        url = reverse('verify_email', args=[subscriber.id])
        return f'{settings.BASE_URL}{url}'

    def send_verification_email(self, subscriber, verification_link):
        subject = 'Please verify your subscription'
        message = f'Hi {subscriber.email}, please click on the link below to verify your subscription:\n\n{verification_link}'
        from_email = settings.DEFAULT_FROM_EMAIL
        content = Content("text/plain", message)
        mail = Mail(from_email=from_email, subject=subject, to_emails=subscriber.email, plain_text_content=content)
        try:
            sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
            sg.send(mail)
        except Exception as e:
            pass