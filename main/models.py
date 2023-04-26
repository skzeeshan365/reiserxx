from django.db import models
import math
from django.urls import reverse

# Create your models here.
from django.utils.text import slugify


class Category(models.Model):
    category = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    image = models.ImageField(upload_to='pics/', null=True, blank=True)
    slug = models.SlugField(unique=True, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/{self.slug}/"

    def get_posts(self):
        return Post.objects.filter(category=self)


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    description = models.CharField(max_length=1000)
    image = models.ImageField(upload_to='pics/', null=True, blank=True)
    timestamp = models.DateTimeField(max_length=50, auto_now=True)
    slug = models.SlugField(unique=True, editable=False)
    category = models.ForeignKey(Category, related_name='posts', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
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


class Tag(models.Model):
    post = models.ForeignKey(Post, related_name='tags', on_delete=models.CASCADE)
    tag = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, editable=False)

    def __str__(self):
        return self.tag

    def save(self, *args, **kwargs):
        self.slug = slugify(self.tag)
        super().save(*args, **kwargs)

    def get_posts(self):
        return Post.objects.filter(tags__tag=self.tag).exclude(pk=self.pk)
