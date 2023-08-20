from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import Post  # Import your Post model

class BlogFeed(Feed):
    title = "ReiserX"  # Your feed's title
    link = "https://www.reiserx.com/blog/"  # URL for the feed
    description = "Latest posts from ReiserX"  # Feed's description

    def items(self):
        return Post.objects.filter(draft=False)  # Filter published posts

    def item_title(self, item):
        return item.title  # Title of each post

    def item_description(self, item):
        return item.description  # Description of each post

    def item_link(self, item):
        return reverse('open', args=[item.author.username, item.slug])  # Link to each post

    def item_pubdate(self, item):
        return item.timestamp  # Publish date of each post
