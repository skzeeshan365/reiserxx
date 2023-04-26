from django.contrib import admin

from .forms import PostForm
from .models import Post, Tag, Category, Comment
from django import forms

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
