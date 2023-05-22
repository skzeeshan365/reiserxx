import json
import math
import os
import random
import re
import uuid

from django.contrib.auth.models import User, AbstractUser
from django.core.validators import MaxLengthValidator
from django.db import IntegrityError
from django.db import models, transaction
# Create your models here.
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.http import urlencode
from django.utils.text import slugify
from google.cloud import translate
from google.oauth2 import service_account


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
        return Post.objects.filter(category=self, draft=False)


class Tag(models.Model):
    tag = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, editable=False)

    def __str__(self):
        return self.tag

    def save(self, *args, **kwargs):
        self.slug = slugify(self.tag)
        super().save(*args, **kwargs)

    def get_posts(self):
        return Post.objects.filter(tags__tag=self.tag, draft=False).exclude(pk=self.pk)[:3]


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    description = models.CharField(max_length=1000)
    image = models.ImageField(upload_to='thumbnail/', null=True, blank=True)
    timestamp = models.DateTimeField(max_length=50, auto_now=True)
    slug = models.SlugField(unique=True, editable=False, max_length=255)
    category = models.ForeignKey(Category, related_name='posts', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='author', on_delete=models.CASCADE, default=None)
    tags = models.ManyToManyField(Tag, related_name='posts')
    draft = models.BooleanField(default=False)
    is_ad = models.BooleanField(default=False)

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
        if self.timestamp:
            return self.timestamp.strftime('%d %B %Y')
        else:
            return 'now'

    def get_tags(self):
        return self.tags.values_list('tag', flat=True)

    def get_reading_time(self, words_per_minute=200):
        word_count = len(self.content.split())
        reading_time = math.ceil(word_count / words_per_minute)
        return reading_time

    def get_content(self):
        content = self.content

        # Calculate the word count
        word_count = len(re.findall(r'\w+', content))

        # Determine the number of ads based on word count
        ad_count = min(word_count // 200, 5)  # Insert one ad per 1000 words, up to a maximum of 5 ads

        # Insert the AdSense ad code randomly
        ad_code = '''<div class="adsense-ad">
            <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1588658066763563"
            crossorigin="anonymous"></script>
            <ins class="adsbygoogle"
                 style="display:block; text-align:center;"
                 data-ad-layout="in-article"
                 data-ad-format="fluid"
                 data-ad-client="ca-pub-1588658066763563"
                 data-ad-slot="4101024703"></ins>
            <script>
            (adsbygoogle = window.adsbygoogle || []).push({});
            </script>
        </div>'''

        # Split the content into paragraphs
        paragraphs = re.split(r'(</?p>)', content)

        # Remove empty strings and paragraph tags from the paragraphs list
        paragraphs = [p for p in paragraphs if p.strip() and not re.match(r'</?p>', p)]

        # Generate random indices to insert ads
        ad_positions = random.sample(range(len(paragraphs)), ad_count)
        ad_positions.sort(reverse=True)  # Sort in reverse order to preserve indices after inserting ads

        # Insert the ad code at the random positions
        for position in ad_positions:
            # Check if the paragraph is a heading
            if not re.match(r'<h\d>', paragraphs[position]):
                paragraphs.insert(position, ad_code)

        # Join the modified paragraphs back into a single string
        content = ''.join(paragraphs)
        return content

    def get_comments(self):
        return self.comments.filter(post=self.pk)

    def get_related_posts(self):
        return Post.objects.filter(tags__tag__in=self.get_tags(), draft=False).exclude(slug=self.slug).distinct()[:3]

    def get_author_name(self):
        return self.author.get_username()

    @staticmethod
    def search_by_title(query):
        return Post.objects.filter(title__icontains=query, draft=False).only('title', 'description', 'content', 'image',
                                                                             'timestamp',
                                                                             'author')

    @classmethod
    def get_posts_by_user(cls, user):
        return cls.objects.filter(author=user, draft=False).only('title', 'description', 'content', 'image',
                                                                 'timestamp')

    def translate(self, code):

        # calling up google vision json file
        with open(r"main/key.json") as f:
            credentials_info = json.load(f)
        credentials = service_account.Credentials.from_service_account_info(credentials_info)

        # Initialize the Google Cloud Translation API client
        client = translate.TranslationServiceClient(credentials=credentials)
        response = client.translate_text(
            contents=[self.title, self.content+""
                                               "Translated by AI"],
            target_language_code=code,
            parent='projects/' + os.getenv('project_id')
        )

        # Get the translated text from the response and display it
        translations = response.translations
        self.title = translations[0].translated_text
        self.content = translations[1].translated_text

        return self


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(validators=[MaxLengthValidator(500)])
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)


class Contact(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(max_length=50, auto_now=True)


class Subscriber(models.Model):
    id = models.CharField(primary_key=True, editable=False, unique=True, max_length=36)
    email = models.EmailField(unique=True)
    verified = models.BooleanField(default=False)


@receiver(pre_save, sender=Subscriber)
def subscriber_pre_save(sender, instance, **kwargs):
    if not instance.id:
        instance.id = str(uuid.uuid4())
