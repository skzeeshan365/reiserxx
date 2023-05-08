from django.core.validators import MaxLengthValidator
from django.db import models, transaction
import math
from django.contrib.auth.models import User, AbstractUser

# Create your models here.
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.http import urlencode
from django.utils.text import slugify
from django.db import IntegrityError
from meta.models import ModelMeta


class Category(models.Model):
    category = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    image = models.ImageField(upload_to='category/', null=True, blank=True)
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
    image = models.ImageField(upload_to='thumbnail/', null=True, blank=True)
    timestamp = models.DateTimeField(max_length=50, auto_now=True)
    slug = models.SlugField(unique=True, editable=False)
    category = models.ForeignKey(Category, related_name='posts', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='author', on_delete=models.CASCADE, default=None)
    tags = models.ManyToManyField(Tag, related_name='posts')

    def save(self, *args, **kwargs):
        if not self.pk:
            # new object, set slug
            self.slug = slugify(self.title)

            while True:
                try:
                    with transaction.atomic():
                        # use select_for_update to lock the row during the transaction
                        Post.objects.select_for_update().get(slug=self.slug)
                        self.slug = f"{slugify(self.title)}-{get_random_string(length=10)}"
                except Post.DoesNotExist:
                    break
                except IntegrityError:
                    # duplicate slug, generate a new one
                    self.slug = f"{slugify(self.title)}-{get_random_string(length=10)}"
        else:
            # object is being updated
            # check if title has changed
            old_post = Post.objects.get(pk=self.pk)
            if old_post.title != self.title:
                self.slug = slugify(self.title)
                # check for existing slug and append random string
                while True:
                    try:
                        with transaction.atomic():
                            # use select_for_update to lock the row during the transaction
                            Post.objects.select_for_update().exclude(pk=self.pk).get(slug=self.slug)
                            self.slug = f"{slugify(self.title)}-{get_random_string(length=10)}"
                    except Post.DoesNotExist:
                        break
                    except IntegrityError:
                        # duplicate slug, generate a new one
                        self.slug = f"{slugify(self.title)}-{get_random_string(length=10)}"

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        url = reverse('open', args=[self.author.username, self.slug])
        query_params = urlencode({
            'name': self.title,
            'description': self.description,
            'image': self.image.url,
        })
        return f"{url}?{query_params}"

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
        return self.author.get_username()

    @staticmethod
    def search_by_title(query):
        return Post.objects.filter(title__icontains=query).only('title', 'description', 'content', 'image', 'timestamp', 'author')

    @classmethod
    def get_posts_by_user(cls, user):
        return cls.objects.filter(author=user).only('title', 'description', 'content', 'image', 'timestamp')

    def get_meta(self, default_meta=None, **kwargs):
        meta = super().get_meta(default_meta, **kwargs)

        meta.update({
            'title': self.title,
            'description': self.description,
            'og_title': self.title,
            'og_description': self.description,
            'og_image': self.image.url if self.image else None,
        })

        return meta


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(validators=[MaxLengthValidator(500)])
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)


class Contact(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=70, blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(max_length=50, auto_now=True)