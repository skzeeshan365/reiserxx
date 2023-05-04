import io

import cloudinary
from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile
from tinymce.widgets import TinyMCE

from main.models import Post, Tag, Category
from PIL import Image
from io import BytesIO
import base64
from bs4 import BeautifulSoup
from cloudinary.uploader import upload


def compress(image):
    # Open image using PIL
    img = Image.open(image)

    # Set quality to 80%
    img.save(image, 'JPEG', quality=70)

    # Read the compressed image into memory
    in_memory = io.BytesIO()
    img.save(in_memory, format='JPEG')
    in_memory.seek(0)

    return in_memory


def process_content(content):
    soup = BeautifulSoup(content, 'html.parser')

    # Upload and replace image blobs with corresponding URLs
    for img1 in soup.find_all('img'):
        if 'src' in img1.attrs:
            src = img1.attrs['src']
            if src.startswith('data:image/'):
                # Convert the image blob to an InMemoryUploadedFile
                img_data = src.split(',')[1]
                img_file = BytesIO()
                img_file.write(base64.b64decode(img_data))
                img_file.seek(0)

                # Upload the image to Cloudinary
                result = cloudinary.uploader.upload(compress(img_file), folder='content')

                # Replace the blob with the Cloudinary URL
                img1.attrs['src'] = result['secure_url']

    # Update the post content with the new URLs
    return str(soup)


class CategoryForm(forms.ModelForm):
    image = forms.ImageField(required=False)

    class Meta:
        model = Category
        fields = ['category', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = kwargs.get('instance')
        if instance:
            if instance.image:
                self.fields['image'].initial = instance.image
            else:
                self.fields['image'].initial = None

    def save(self, commit=True):
        category = super().save(commit=False)
        if commit:
            # only save the image if it hasn't been uploaded before
            image = self.cleaned_data.get('image')
            if image != category.image:
                if image:
                    # Compress the image
                    compressed_image = compress(image)

                    # Assign the compressed image as the value for post.image
                    category.image.save(image.name, compressed_image, save=True)

            category.save()

        return category


class PostForm(forms.ModelForm):
    tags = forms.CharField(max_length=255, required=False)
    image = forms.ImageField(required=True)

    content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

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

            tags = self.cleaned_data['tags']
            if tags:
                tag_list = self.clean_tags()
                for tag in tag_list:
                    tag_obj, created = Tag.objects.get_or_create(tag=tag)
                    post.tags.add(tag_obj)

            image = self.cleaned_data.get('image')
            if image:
                # Compress the image
                compressed_image = compress(image)

                # Assign the compressed image as the value for post.image
                post.image.save(image.name, compressed_image, save=True)

            post.content = process_content(post.content)

            post.save()
        return post


class PostFormEdit(forms.ModelForm):
    tags = forms.CharField(max_length=255, required=False)
    image = forms.ImageField(required=True)

    content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

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
            # Update the fields that have changed
            if self.cleaned_data['title'] != post.title:
                post.title = self.cleaned_data['title']
            if self.cleaned_data['content'] != post.content:
                post.content = self.cleaned_data['content']
            if self.cleaned_data['description'] != post.description:
                post.description = self.cleaned_data['description']
            if self.cleaned_data['category'] != post.category:
                post.category = self.cleaned_data['category']

            tag_list = self.clean_tags()
            if tag_list != list(post.tags.values_list('tag', flat=True)):
                post.tags.clear()
                for tag in tag_list:
                    tag_obj, created = Tag.objects.get_or_create(tag=tag)
                    post.tags.add(tag_obj)

            image = self.cleaned_data.get('image')
            if image != post.image:
                if image:
                    # Compress the image
                    compressed_image = compress(image)

                    # Assign the compressed image as the value for post.image
                    post.image.save(image.name, compressed_image, save=True)

            post.content = process_content(post.content)
            post.save()
        return post