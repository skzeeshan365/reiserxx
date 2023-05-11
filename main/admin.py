from django.contrib import admin

from administration.forms import PostForm
from .models import Post, Tag, Category, Comment, Contact, Subscriber


# Register your models here.


class PostInline(admin.StackedInline):
    model = Post


class CategoryAdmin(admin.ModelAdmin):
    inlines = [
        PostInline
    ]


class PostAdmin(admin.ModelAdmin):
    form = PostForm


admin.site.register(Post, PostAdmin)
admin.site.register(Tag)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment)
admin.site.register(Contact)
admin.site.register(Subscriber)
