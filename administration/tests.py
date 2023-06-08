import io
from unittest.mock import patch

from PIL import Image
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from administration.autoGenerate import save_post_with_generated_data
from administration.forms import PostForm, PostFormEdit
from main.models import Post, Tag, Category


# Create your tests here.

def create_image():
    file = io.BytesIO()
    image = Image.new('RGBA', size=(50, 50), color=(155, 0, 0))
    # Convert image to RGB mode
    image = image.convert('RGB')
    image.save(file, 'jpeg')
    file.name = 'test.jpg'
    file.seek(0)
    return file


class PostCreateViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('post_new')
        self.user = User.objects.create_superuser(
            username='testuser',
            email='testuser@example.com',
            password='testpass'
        )
        self.category = Category.objects.create(category='general')
        self.image = SimpleUploadedFile(name='test.jpg', content=create_image().read(), content_type='image/jpeg')

    def tear_down(self):
        for post in Post.objects.all():
            if 'test' in post.title.lower():
                post.image.delete()
                post.delete()

    def test_create_post(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url, data={
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-title': 'Test Post',
            'form-0-content': 'This is a test post.',
            'form-0-description': 'Test description',
            'form-0-category': self.category.pk,
            'form-0-tags': 'test, post',
            'form-0-image': self.image
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('post_new'))
        post = Post.objects.get(title='Test Post')
        self.assertEqual(post.content, 'This is a test post.')
        self.assertEqual(post.description, 'Test description')
        self.assertEqual(post.category.category, self.category.category)
        self.assertEqual(post.author, self.user)
        self.assertIsNotNone(post.tags)
        self.assertListEqual(list(post.tags.order_by('tag').values_list('tag', flat=True)), ['post', 'test'])
        self.tear_down()

    def test_invalid_form_data(self):
        # Test case for invalid form data
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url, data={
            'title': '',  # empty title field
            'content': 'This is a test post.',
            'description': 'Test description',
            'category': 'general',
            'tags': 'test, post',
            'image': self.image
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.tear_down()

    def test_empty_image_field(self):
        # Test case for empty image field
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url, data={
            'title': 'Test Post',
            'content': 'This is a test post.',
            'description': 'Test description',
            'category': 'general',
            'tags': 'test, post',
            'image': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.tear_down()

    def test_unauthenticated_user_cannot_create_post(self):
        response = self.client.post(self.url, data={
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-title': 'Test Post',
            'form-0-content': 'This is a test post.',
            'form-0-description': 'Test description',
            'form-0-category': 'general',
            'form-0-tags': 'test, post',
            'form-0-image': self.image
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.filter(title='Test Post').count(), 0)
        self.tear_down()


class PostFormTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(category='Test')
        self.image = SimpleUploadedFile(name='test.jpg', content=create_image().read(), content_type='image/jpeg')
        self.post_data = {
            'title': 'Test Post',
            'content': 'This is a test post.',
            'description': 'Test description',
            'category': self.category.pk,
            'tags': 'test, post',
            'draft': True
        }

    def test_valid_post_form(self):
        data = self.post_data.copy()
        data['image'] = self.image
        form = PostForm(data=data, files=data)
        self.assertTrue(form.is_valid())

    def test_invalid_post_form(self):
        data = self.post_data.copy()
        data['category'] = ''
        form = PostForm(data=data)
        self.assertFalse(form.is_valid())

    def test_clean_tags(self):
        form = PostForm()
        form.cleaned_data = {'tags': 'test1, test2, test3'}
        tags = form.clean_tags()
        self.assertEqual(tags, ['test1', 'test2', 'test3'])

    def test_save_post_with_image(self):
        form = PostForm(data=self.post_data, files={
            'image': self.image
        })
        self.assertTrue(form.is_valid())

        post = form.save(commit=False)
        post.author = self.user
        post.save()
        form.save()
        self.assertTrue(post.pk)
        self.assertIsNotNone(post.image)
        self.assertEqual(post.tags.count(), 2)

        post.image.delete()
        post.delete()

    def test_save_post_with_tags(self):
        tag1 = Tag.objects.create(tag='test1')
        tag2 = Tag.objects.create(tag='test2')

        self.post_data['tags'] = 'test1, test2'

        form = PostForm(data=self.post_data, files={
            'image': self.image
        })
        self.assertTrue(form.is_valid())

        post = form.save(commit=False)
        post.author = self.user
        post.save()
        form.save()

        self.assertEqual(post.tags.count(), 2)
        self.assertIn(tag1, post.tags.all())
        self.assertIn(tag2, post.tags.all())

        # Clean up
        post.image.delete()
        post.delete()

    def test_save_post(self):
        # Create a form with post data and image
        form = PostForm(data=self.post_data, files={'image': self.image})
        self.assertTrue(form.is_valid())

        # Save the form
        post = form.save(commit=False)
        post.author = self.user
        post.save()
        form.save()

        # Check that the post was created and saved correctly
        self.assertTrue(Post.objects.filter(title='Test post').exists())
        self.assertEqual(post.content, 'This is a test post.')
        self.assertEqual(post.tags.count(), 2)
        self.assertTrue(post.image)

        # Clean up
        post.image.delete()
        post.delete()

    def test_save_post_with_empty_content(self):
        form_data = {
            'title': 'Test Post',
            'content': '',
            'description': 'Test description',
            'category': self.category.pk,
            'tags': 'test1, test2',
            'draft': True
        }
        form = PostForm(data=form_data, files={
            'image': self.image
        })
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)


class PostFormEditTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(category='Test Category')
        self.tag1 = Tag.objects.create(tag='test1')
        self.tag2 = Tag.objects.create(tag='test2')
        self.tag3 = Tag.objects.create(tag='test3')
        self.post_data = {
            'title': 'Test Post',
            'content': 'This is a test post.',
            'description': 'Test description',
            'category': self.category.pk,
            'tags': 'test1, test2',
        }
        self.post = Post.objects.create(
            author=self.user,
            title='Test Post',
            content='This is a test post.',
            description='Test description',
            category=self.category
        )
        self.post.tags.add(self.tag1, self.tag2)

    def test_edit_post_with_valid_data(self):
        form_data = {
            'title': 'Edited Test Post',
            'content': 'This is an edited test post.',
            'description': 'Edited test description',
            'category': self.category.pk,
            'tags': 'test2, test3',
        }
        image = SimpleUploadedFile(name='test.jpg', content=create_image().read(), content_type='image/jpeg')
        form = PostFormEdit(data=form_data, files={'image': image}, instance=self.post)
        self.assertTrue(form.is_valid())

        post = form.save()
        self.assertEqual(post.pk, self.post.pk)
        self.assertEqual(post.title, 'Edited Test Post')
        self.assertEqual(post.content, 'This is an edited test post.')
        self.assertEqual(post.description, 'Edited test description')
        self.assertEqual(post.category, self.category)
        self.assertEqual(post.tags.count(), 2)
        self.assertIn(self.tag2, post.tags.all())
        self.assertIn(Tag.objects.get(tag='test3'), post.tags.all())
        self.assertTrue(post.image)

        self.post.image.delete()
        self.post.delete()
        post.image.delete()

    def test_edit_post_with_invalid_data(self):
        form_data = {
            'title': '',
            'content': '',
            'description': '',
            'category': '',
            'tags': '',
        }
        form = PostFormEdit(data=form_data, instance=self.post)
        self.assertFalse(form.is_valid())
        self.post.image.delete()
        self.post.delete()

    def test_save_method_with_valid_data(self):
        # create form data
        form_data = {
            'title': 'Updated Test Post',
            'content': 'This is an updated test post.',
            'description': 'Updated test description',
            'category': self.category.pk,
            'tags': 'test2, test3',
        }

        # create post form instance
        form = PostFormEdit(data=form_data, instance=self.post, files={
            'image': SimpleUploadedFile(name='test.jpg', content=create_image().read(), content_type='image/jpeg')
        })

        # check if form is valid
        self.assertTrue(form.is_valid())

        # save the form
        form.save()

        # refresh post instance from database
        self.post.refresh_from_db()

        # check if the post instance was updated correctly
        self.assertEqual(self.post.title, form_data['title'])
        self.assertEqual(self.post.content, form_data['content'])
        self.assertEqual(self.post.description, form_data['description'])
        self.assertEqual(self.post.category.pk, form_data['category'])
        self.assertEqual(self.post.tags.count(), 2)

        # check that the tag 'test3' was added to the post
        tag3 = Tag.objects.get(tag='test3')
        self.assertIn(tag3, self.post.tags.all())

        # cleanup
        self.post.image.delete()
        self.post.delete()
        self.tag1.delete()
        self.tag2.delete()
        tag3.delete()


class PostEditViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(
            username='testuser',
            email='testuser@example.com',
            password='testpass'
        )
        self.category = Category.objects.create(category='Test Category')
        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post.',
            author=self.user,
            category=self.category
        )
        self.post_url = reverse('post_edit', args=[self.post.slug])
        self.login_url = reverse('login')
        self.image = SimpleUploadedFile(name='test.jpg', content=create_image().read(), content_type='image/jpeg')

    def test_post_edit_view_with_valid_data(self):
        self.client.login(username='testuser', password='testpass')
        form_data = {
            'title': 'Updated Test Post',
            'content': 'This is an updated test post.',
            'description': 'Updated test description',
            'category': self.post.category.pk,
            'tags': 'test2, test3',
            'image': self.image
        }
        response = self.client.post(self.post_url, data=form_data, format='multipart')
        self.assertRedirects(response, reverse('post_list'))
        updated_post = Post.objects.get(pk=self.post.pk)
        self.assertEqual(updated_post.title, form_data['title'])
        self.assertEqual(updated_post.content, form_data['content'])
        self.assertEqual(updated_post.description, form_data['description'])
        self.assertEqual(updated_post.category.pk, form_data['category'])
        self.assertEqual(updated_post.tags.count(), 2)
        self.assertEqual(list(updated_post.tags.values_list('tag', flat=True)), ['test2', 'test3'])

        self.post.image.delete()
        self.post.delete()
        updated_post.delete()

    def test_post_edit_view_with_invalid_data(self):
        self.client.login(username='testuser', password='testpass')
        form_data = {
            'title': '',
            'content': 'This is an updated test post.',
            'description': 'Updated test description',
            'category': self.post.category.pk,
            'tags': 'test2, test3',
            'image': self.image
        }
        response = self.client.post(self.post_url, data=form_data, format='multipart')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        updated_post = Post.objects.get(pk=self.post.pk)
        self.assertNotEqual(updated_post.title, form_data['title'])
        self.assertNotEqual(updated_post.content, form_data['content'])
        self.assertNotEqual(updated_post.description, form_data['description'])
        self.assertEqual(updated_post.category.pk, form_data['category'])
        self.assertEqual(updated_post.tags.count(), 0)

        self.post.image.delete()
        self.post.delete()
        updated_post.image.delete()
        updated_post.delete()

    def test_post_edit_view_with_unauthorized_user(self):
        form_data = {
            'title': 'Updated Test Post',
            'content': 'This is an updated test post.',
            'description': 'Updated test description',
            'category': self.post.category.pk,
            'tags': 'test2, test3',
        }
        response = self.client.post(self.post_url, data=form_data, files={'image': self.image})
        self.assertEqual(response.status_code, 302)

        self.post.image.delete()
        self.post.delete()


class PostSaveTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(category='Test')
        self.image = SimpleUploadedFile(name='test.jpg', content=create_image().read(), content_type='image/jpeg')

        # Create a post form
        self.post_data = {
            'content': 'Generated Content',
            'description': 'Generated Description',
            'title': 'Generated Title',
            'category': self.category.pk,
            'tags': 'test, post'
        }

    def test_valid_post_form(self):
        data = self.post_data.copy()
        data['image'] = self.image
        form = PostForm(data=data, files=data)
        self.assertTrue(form.is_valid())

    def test_save_post_with_generated_data(self):
        data = self.post_data.copy()
        data['image'] = self.image
        form = PostForm(data=data, files=data)

        # Validate the form
        self.assertTrue(form.is_valid(), form.errors.as_data())

        # Save the post
        post = form.save(commit=False)
        post.author = self.user
        post.save()
        form.save_m2m()

        # Verify that the post is created with the generated data
        self.assertEqual(post.content, "Generated Content")
        self.assertEqual(post.description, "Generated Description")
        self.assertEqual(post.title, "Generated Title")
        self.assertIsNotNone(post.image)
        self.assertEqual(post.category, self.category)
        self.assertEqual(post.author, self.user)

        # Clean up the test objects
        post.image.delete()
        post.delete()
        self.user.delete()
        self.category.delete()
