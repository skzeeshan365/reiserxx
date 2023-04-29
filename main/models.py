from django.core.validators import MaxLengthValidator
from django.db import models
import math
from django.contrib.auth.models import User
from PIL import Image
import io
from django.core.files.uploadedfile import InMemoryUploadedFile

# Create your models here.
from django.utils.crypto import get_random_string
from django.utils.text import slugify


def compress(image):
    # Open image using PIL
    img = Image.open(image)

    # Set quality to 80%
    img.save(image, 'JPEG', quality=80)

    # Read the compressed image into memory
    in_memory = io.BytesIO()
    img.save(in_memory, format='JPEG')
    in_memory.seek(0)

    return in_memory


class Category(models.Model):
    category = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    image = models.ImageField(upload_to='pics/', null=True, blank=True)
    slug = models.SlugField(unique=True, editable=False)

    def __str__(self):
        return self.category

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/{self.slug}/"

    def get_posts(self):
        return Post.objects.filter(category=self)


class Tag(models.Model):
    tag = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, editable=False)

    def __str__(self):
        return self.tag

    def save(self, *args, **kwargs):
        self.slug = slugify(self.tag)
        super().save(*args, **kwargs)

    def get_posts(self):
        return Post.objects.filter(tags__tag=self.tag).exclude(pk=self.pk)


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    description = models.CharField(max_length=1000)
    image = models.ImageField(upload_to='pics/', null=True, blank=True)
    timestamp = models.DateTimeField(max_length=50, auto_now=True)
    slug = models.SlugField(unique=True, editable=False)
    category = models.ForeignKey(Category, related_name='posts', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='author', on_delete=models.CASCADE, default=None)
    tags = models.ManyToManyField(Tag, related_name='posts')

    def save(self, *args, **kwargs):
        # slugify the title and save the post
        self.slug = slugify(self.title)

        # check for existing slug and append random string
        if Post.objects.filter(slug=self.slug).exists():
            self.slug = f"{self.slug}-{get_random_string(length=6)}"

        if self.image:
            # Compress the image and save it
            compressed_image = compress(self.image)
            self.image = InMemoryUploadedFile(compressed_image, 'ImageField', self.image.name, 'image/jpeg',
                                              compressed_image.tell, None)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/posts/{self.slug}/"

    def get_date(self):
        # Format the date_published field as "22 July 2017"
        return self.timestamp.strftime('%d %B %Y')

    def get_tags(self):
        return self.tags.values_list('tag', flat=True)

    def get_reading_time(self, words_per_minute=200):
        word_count = len(self.content.split())
        reading_time = math.ceil(word_count / words_per_minute)
        return reading_time

    def get_content(self):
        return self.content

    def get_comments(self):
        return self.comments.filter(post=self.pk)

    def get_related_posts(self):
        return Post.objects.filter(tags__tag__in=self.get_tags()).exclude(slug=self.slug).distinct()

    def get_author_name(self):
        return slugify(self.author.get_full_name())

    @staticmethod
    def search_by_title(query):
        return Post.objects.filter(title__icontains=query).only('title', 'description', 'content', 'image', 'timestamp', 'author')

    @classmethod
    def get_posts_by_user(cls, user):
        return cls.objects.filter(author=user).only('title', 'description', 'content', 'image', 'timestamp')


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(validators=[MaxLengthValidator(500)])
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
