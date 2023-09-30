from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils import feedgenerator

from .models import Post  # Import your Post model


class BlogFeed(Feed):
    title = "ReiserX"  # Your feed's title
    link = "https://www.reiserx.com/blog/"  # URL for the feed
    description = "Latest posts from ReiserX"  # Feed's description
    template_name = "main/partials/postlist.html"  # Use your custom template

    def items(self):
        return Post.objects.filter(draft=False).only('title', 'description', 'image', 'timestamp_modified', 'author').order_by('-timestamp_modified')  # Filter published posts

    def item_title(self, item):
        return item.title  # Title of each post

    def item_description(self, item):
        return item.description  # Description of each post

    def item_link(self, item):
        return reverse('open', args=[item.author.username, item.slug])  # Link to each post

    def item_enclosures(self, item):
        return [feedgenerator.Enclosure(item.image.url, str(item.image.size),
                                        'image/{}'.format(item.image.name.split('.')[-1]))]

    def item_pubdate(self, item):
        return item.timestamp_modified  # Publish date of each post
