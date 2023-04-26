from django.test import TestCase
from django.urls import reverse
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