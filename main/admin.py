from django.contrib import admin

from administration.forms import PostForm
from .models import Post, Tag, Category, Comment, Contact, Subscriber, Reply


# Register your models here.


class PostInline(admin.StackedInline):
    model = Post


class CategoryAdmin(admin.ModelAdmin):
    inlines = [
        PostInline
    ]


class PostAdmin(admin.ModelAdmin):
    form = PostForm


class ReplyInline(admin.StackedInline):
    model = Reply


class CommentAdmin(admin.ModelAdmin):
    inlines = [
        ReplyInline
    ]


admin.site.register(Post, PostAdmin)
admin.site.register(Tag)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Reply)
admin.site.register(Contact)
admin.site.register(Subscriber)
