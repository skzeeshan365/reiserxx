import json

from django.test import TestCase, Client
from django.urls import reverse

from .forms import ContactForm
from .models import Category, Post
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io


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
        self.category = Category.objects.create(
            category='Technology', slug='technology', description='Tech news'
        )
        self.post1 = Post.objects.create(
            title='Post 1', content='Content 1', category=self.category,
            image=self.create_image()
        )
        print('Post 1 image:', self.post1.image)
        self.post2 = Post.objects.create(
            title='Post 2', content='Content 2', category=self.category,
            image=self.create_image()
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


class ContactFormTestCase(TestCase):

    def test_valid_form(self):
        form_data = {
            'username': 'John Doe',
            'email': 'johndoe@example.com',
            'message': 'Hello, this is a test message'
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_empty_fields(self):
        form_data = {
            'username': '',
            'email': '',
            'message': ''
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_email(self):
        form_data = {
            'username': 'John Doe',
            'email': 'invalidemail',
            'message': 'Hello, this is a test message'
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_long_message(self):
        form_data = {
            'username': 'John Doe',
            'email': 'johndoe@example.com',
            'message': 'a' * 1600
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