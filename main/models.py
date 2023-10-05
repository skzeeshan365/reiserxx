import json
import math
import random
import re
import uuid

from bs4 import BeautifulSoup
from django.contrib.auth.models import User, AbstractUser
from django.core.validators import MaxLengthValidator
from django.db import IntegrityError
from django.db import models, transaction
# Create your models here.
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.http import urlencode
from django.utils.text import slugify
from google.cloud import translate
from google.oauth2 import service_account

from main import utils


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
        self.slug = slugify(self.tag.lower())
        super().save(*args, **kwargs)

    def get_posts(self):
        return Post.objects.filter(tags__tag=self.tag, draft=False).exclude(pk=self.pk)


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    description = models.CharField(max_length=1000)
    image = models.ImageField(upload_to='thumbnail/', null=True, blank=True)
    timestamp_created = models.DateTimeField(auto_now_add=True)
    timestamp_modified = models.DateTimeField(auto_now=True)
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

    def get_absolute_post_url(self, request):
        relative_url = reverse('open', args=[self.author.username, self.slug])
        absolute_url = request.build_absolute_uri(relative_url)
        return absolute_url

    def get_date(self):
        # Format the date_published field as "22 July 2017"
        if self.timestamp_created:
            return self.timestamp_created.strftime('%d %B, %Y')
        else:
            return 'now'

    def get_tags(self):
        return self.tags.values_list('tag', flat=True)

    def get_reading_time(self, words_per_minute=265):
        soup = BeautifulSoup(self.content, 'html.parser')

        # Extract the plain text from the HTML
        readable_text = soup.get_text(separator=' ')

        # Calculate the word count from the readable text
        word_count = len(readable_text.split())

        # Calculate the reading time in minutes
        reading_time = math.ceil(word_count / words_per_minute)

        return reading_time

    def get_content_preview(self):
        return self.content

    def get_content_text(self):
        soup = BeautifulSoup(self.content, 'html.parser')
        text = soup.get_text()

        # Remove unnecessary whitespace and line breaks
        text = ' '.join(text.split())
        return str(text)

    def get_content(self):
        content = self.content

        soup = BeautifulSoup(content, 'html.parser')

        # Find all image tags
        for img in soup.find_all('img'):
            alt_text = img.get('alt')
            if alt_text:
                # Create a new paragraph tag with the caption
                caption_tag = soup.new_tag('p')
                caption_tag.string = alt_text

                # Add a CSS class to the caption tag
                caption_tag['class'] = 'image-caption'

                # Add a CSS style to align the caption to the center and override the margin
                caption_tag['style'] = 'text-align: center; margin-top: 5px;'

                # Wrap the image tag with a div to apply the margin to the div instead of the paragraph tag
                img.wrap(soup.new_tag('div', style='margin: unset;'))

                # Append the caption tag after the image tag
                img.insert_after(caption_tag)

        # Calculate the word count
        word_count = len(re.findall(r'\w+', str(soup)))

        # Determine the number of ads based on word count
        ad_count = min(word_count // 200, 5)  # Insert one ad per 1000 words, up to a maximum of 5 ads

        # Insert the AdSense ad code randomly
        ad_code = '''
        <div class="adsense-ad" style="margin-bottom: 8px">
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
        </div>
        '''

        # Split the content into paragraphs and preserve the surrounding tags
        paragraphs = re.split(r'(</?(?:p|div|h\d|img).*?>)', str(soup))

        # Generate random indices to insert ads
        ad_positions = random.sample(range(len(paragraphs)), ad_count)
        ad_positions.sort(reverse=True)  # Sort in reverse order to preserve indices after inserting ads

        # Insert the ad code at the random positions
        for position in ad_positions:
            paragraphs.insert(position + 1, ad_code)

        # Join the modified paragraphs back into a single string
        content = ''.join(paragraphs)

        return content

    def get_comments(self):
        return self.comments.filter(post=self.pk)

    def get_related_posts(self):
        return Post.objects.filter(tags__tag__in=self.get_tags(), draft=False).exclude(slug=self.slug).distinct()[:6]

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
        try:
            existing_translation = TranslatedPost.objects.get(post=self, language_code=code)
            self.title = existing_translation.translated_title
            self.description = existing_translation.translated_description
            self.content = existing_translation.translated_content
        except TranslatedPost.DoesNotExist:
            # calling up google vision json file
            with open(r"main/key.json") as f:
                credentials_info = json.load(f)
            credentials = service_account.Credentials.from_service_account_file(r"main/key.json")

            # Initialize the Google Cloud Translation API client
            client = translate.TranslationServiceClient(credentials=credentials)

            response = client.translate_text(
                contents=[self.title, self.description, self.content + ""
                                                                       "Translated by AI"],
                target_language_code=code,
                parent='projects/' + credentials_info['project_id']
            )

            # Get the translated text from the response and display it
            translations = response.translations
            self.title = translations[0].translated_text
            self.description = translations[1].translated_text
            self.content = translations[2].translated_text

            translation = TranslatedPost(
                post=self,
                language_code=code,
                translated_title=self.title,
                translated_description=self.description,
                translated_content=self.content
            )
            translation.save()

        return self

    def get_summary(self):
        try:
            return self.summary.get(post=self).summary
        except Summary.DoesNotExist:
            return None


class Summary(models.Model):
    post = models.ForeignKey(Post, related_name='summary', on_delete=models.CASCADE)
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Summary for {self.post.title}"


class TranslatedPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='translated_version')
    language_code = models.CharField(max_length=10)
    translated_title = models.CharField(max_length=200)
    translated_description = models.CharField(max_length=1000)
    translated_content = models.TextField()

    is_ad = False

    def __str__(self):
        return f"{self.post.title} ({self.language_code})"

    class Meta:
        unique_together = ['post', 'language_code']


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(validators=[MaxLengthValidator(500)])
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def ordered_replies(self):
        return self.replies.all().order_by('-timestamp')


class Reply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField(validators=[MaxLengthValidator(500)])
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)


class Contact(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(max_length=50, auto_now=True)


@receiver(post_save, sender=Contact)
def send_contact_email(sender, instance, created, **kwargs):
    if created:
        subject = "A New Message Is Received"

        message = render_to_string('main/About/contact_email_template.html', {
            'sender_name': instance.username,
            'email': instance.email,
            'message': instance.message,
        })

        superusers = User.objects.filter(is_superuser=True)
        to_email = [user.email for user in superusers]

        try:
            utils.send_email(subject=subject, message=message, to_email=to_email)
        except Exception as e:
            pass


class Subscriber(models.Model):
    id = models.CharField(primary_key=True, editable=False, unique=True, max_length=36)
    email = models.EmailField(unique=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.email}"


@receiver(pre_save, sender=Subscriber)
def subscriber_pre_save(sender, instance, **kwargs):
    if not instance.id:
        instance.id = str(uuid.uuid4())
