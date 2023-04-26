from django import forms
from .models import Comment, Post, Tag
import re
from django.core.exceptions import ValidationError


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


class PostForm(forms.ModelForm):
    tags = forms.CharField(max_length=255, required=False)
    image = forms.ImageField(required=True)

    class Meta:
        model = Post
        fields = ['title', 'content', 'description', 'category']

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if tags:
            if isinstance(tags, str):
                tag_list = [tag.strip() for tag in tags.split(',')]
            else:
                tag_list = [tag.strip() for tag in tags]
            return tag_list
        return []

    def save(self, commit=True):
        post = super().save(commit=False)
        if commit:
            post.save()

            tags = self.cleaned_data['tags']
            if tags:
                tag_list = self.clean_tags()
                for tag in tag_list:
                    tag_obj, created = Tag.objects.get_or_create(tag=tag)
                    post.tags.add(tag_obj)

            image = self.cleaned_data.get('image')
            if image:
                post.image = image
                post.save()

        return post