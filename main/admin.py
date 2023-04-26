from django.contrib import admin
from .models import Post, Tag, Category

# Register your models here.


class TagInline(admin.StackedInline):
    model = Tag


class PostInline(admin.StackedInline):
    model = Post


class PostAdmin(admin.ModelAdmin):
    inlines = [
        TagInline
    ]


class CategoryAdmin(admin.ModelAdmin):
    inlines = [
        PostInline
    ]


admin.site.register(Post, PostAdmin)
admin.site.register(Tag)
admin.site.register(Category, CategoryAdmin)
