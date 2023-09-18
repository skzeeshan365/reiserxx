import io
import json

from PIL import Image
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import forms
from django.test import TestCase, Client
from django.urls import reverse

from administration.tests import create_image
from djangoProject1 import settings
from .forms import ContactForm, SubscriberForm
from .models import Category, Post, Tag, Subscriber


class SearchByCategoryTest(TestCase):

    def create_image(self):
        file = io.BytesIO()
        image = Image.new('RGBA', size=(50, 50), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        print('Created image:', file)
        return SimpleUploadedFile('test.png', file.getvalue())

    def setUp(self):
        self.user = User.objects.create_superuser(
            username='testuser',
            email='testuser@example.com',
            password='testpass'
        )
        self.category = Category.objects.create(
            category='Technology', slug='technology', description='Tech news'
        )
        self.post1 = Post.objects.create(
            title='Post 1', content='Content 1', category=self.category,
            image=self.create_image(),
            author=self.user
        )
        print('Post 1 image:', self.post1.image)
        self.post2 = Post.objects.create(
            title='Post 2', content='Content 2', category=self.category,
            image=self.create_image(),
            author=self.user
        )
        print('Post 2 image:', self.post2.image)

    def test_search_by_category(self):
        url = reverse('search_by_category', args=[self.category.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post1.title)
        self.assertContains(response, self.post2.title)
        self.assertContains(response, self.category.category)
        self.assertContains(response, self.category.description)
        self.post1.image.delete()
        self.post2.image.delete()


class ContactFormTestCase(TestCase):

    def test_valid_form(self):
        form_data = {
            'username': 'John Doe',
            'email': 'skzeeshan3650@gmail.com',
            'message': 'Hello, this is a test message',
            'recaptcha_response': 'valid_token'
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_empty_fields(self):
        form_data = {
            'username': '',
            'email': '',
            'message': '',
            'recaptcha_response': ''
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_email(self):
        form_data = {
            'username': 'John Doe',
            'email': 'invalidemail',
            'message': 'Hello, this is a test message',
            'recaptcha_response': 'valid_token'
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_long_message(self):
        form_data = {
            'username': 'John Doe',
            'email': 'johndoe@example.com',
            'message': 'a' * 1600,
            'recaptcha_response': 'valid_token'
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())


class ContactFormViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('contact')

    def test_contact_form_valid(self):
        form_data = {
            'username': 'Test User',
            'email': 'test@example.com',
            'message': 'Test message',
            'recaptcha_response': 'valid_token'
        }
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertEqual(json_response['status'], 'error')
        self.assertEqual(json_response['message'], 'Invalid reCAPTCHA. Please try again.')

    def test_contact_form_invalid(self):
        form_data = {
            'username': '',
            'email': '',
            'message': '',
            'recaptcha_response': ''
        }
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertEqual(json_response['status'], 'error')

    def test_contact_form_bot(self):
        form_data = {
            'username': 'Bot',
            'email': 'bot@example.com',
            'message': 'I am a bot',
            'recaptcha_response': '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WPeGz'
        }
        response = self.client.post(self.url, form_data)
        json_response = json.loads(response.content)
        self.assertEqual(json_response['status'], 'error')


class PostTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username='testuser',
            email='testuser@example.com',
            password='testpass'
        )
        self.category = Category.objects.create(category='Test')
        self.image = SimpleUploadedFile(name='test.jpg', content=create_image().read(), content_type='image/jpeg')
        self.post1 = Post.objects.create(
            title='Test Post 1',
            content='This is a test post.',
            description='Test description',
            category=self.category,
            author=self.user
        )
        self.tag = Tag.objects.create(tag='test1')
        self.post1.tags.add(self.tag)

    def test_save_new_post(self):
        self.client.login(username='testuser', password='testpass')
        post3 = Post(title='Test Post 3',
                     content='This is a test post.',
                     description='Test description',
                     category=self.category,
                     author=self.user
                     )
        post3.save()
        post3.tags.add(self.tag)
        post3.save()
        self.assertEqual(post3.slug, 'test-post-3')
        post3.image.delete()

    def test_save_new_post_with_same_title(self):
        post3 = Post(title='Test Post 1',
                     content='This is a test post.',
                     description='Test description',
                     category=self.category,
                     author=self.user
                     )
        post3.save()
        post3.tags.add(self.tag)
        post3.save()
        self.assertNotEqual(post3.slug, 'test-post-1')
        self.assertTrue(post3.slug.startswith('test-post-1'))
        post3.image.delete()

    def test_update_post_title(self):
        self.post1.title = 'Test Post 1 Updated'
        self.post1.save()
        self.assertEqual(self.post1.slug, 'test-post-1-updated')

    def test_update_post_title_with_same_title(self):
        self.post1.title = 'Test Post 1'
        self.post1.save()
        self.assertEqual(self.post1.slug, 'test-post-1')

    def test_update_post_title_with_duplicate_slug(self):
        post3 = Post.objects.create(title='Test Post 1 Updated',
                                    content='This is a test post.',
                                    description='Test description',
                                    category=self.category,
                                    author=self.user
                                    )
        post3.save()
        post3.tags.add()
        post3.save()
        self.post1.title = 'Test Post 1 Updated'
        self.post1.save()
        self.assertNotEqual(self.post1.slug, post3.slug)
        self.assertTrue(self.post1.slug.startswith('test-post-1-updated'))


class SubscriberFormTestCase(TestCase):
    def setUp(self):
        self.email = 'test@example.com'

    def test_valid_form_submission(self):
        form_data = {'email': self.email, 'recaptcha_response': 'valid_token'}
        form = SubscriberForm(data=form_data)
        self.assertTrue(form.is_valid())
        subscriber = form.save()
        self.assertIsInstance(subscriber, Subscriber)
        self.assertEqual(subscriber.email, self.email)
        self.assertFalse(subscriber.verified)

    def test_already_subscribed_email(self):
        Subscriber.objects.create(email=self.email, verified=True)
        cleaned_data = {'email': self.email, 'recaptcha_response': 'valid_token'}
        form = SubscriberForm()
        form.cleaned_data = cleaned_data
        with self.assertRaises(forms.ValidationError):
            form.clean_email()

    def test_verification_email_sent(self):
        form_data = {'email': self.email, 'recaptcha_response': 'valid_token'}
        form = SubscriberForm(data=form_data)
        subscriber = form.save()
        verification_link = form.get_verification_link(subscriber)
        self.assertIn(settings.BASE_URL, verification_link)
        self.assertIn(str(subscriber.id), verification_link)