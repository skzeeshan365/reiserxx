import io

from django import forms
from django.forms import FileInput
from froala_editor.widgets import FroalaEditor

from main.models import Comment, Post, Tag, Category
from PIL import Image
import re
from django.core.exceptions import ValidationError


class CategoryForm(forms.ModelForm):
    image = forms.ImageField(required=False)

    class Meta:
        model = Category
        fields = ['category', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget.attrs['class'] = 'form-control-file'

        # set initial value for image field if instance has an image
        instance = kwargs.get('instance')
        if instance and instance.image:
            self.initial['image'] = instance.image.name

    def save(self, commit=True):
        category = super().save(commit=False)
        if commit:
            category.save()

            image = self.cleaned_data.get('image')
            if image:
                category.image = image
                category.save()

        return category


class PostForm(forms.ModelForm):
    tags = forms.CharField(max_length=255, required=False)
    image = forms.ImageField(required=True)

    options = {
        'imageUploadParam': 'file',
        'imageAllowedTypes': ['jpeg', 'jpg', 'png', 'gif'],
        'imageMaxSize': 10 * 1024 * 1024,  # 10 MB
    }
    content = forms.CharField(widget=FroalaEditor(options=options))

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            self.fields['tags'].initial = ', '.join([tag.tag for tag in instance.tags.all()])
            if instance.image:
                self.fields['image'].initial = instance.image
            else:
                self.fields['image'].initial = None

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
                with Image.open(image) as img:
                    # Convert the image to RGB format
                    rgb_img = img.convert('RGB')

                    # Save the converted image to a buffer
                    output = io.BytesIO()
                    rgb_img.save(output, format='JPEG', quality=70)
                    output.seek(0)

                    # Assign the buffer as the value for post.image
                    post.image.save(image.name, output, save=True)
        return post