from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404

from .forms import CommentForm
from .models import Post
from .models import Tag
from .models import Category

# Create your views here.


def home(request):
    posts = Post.objects.order_by('-timestamp')[:2]
    all_posts = Post.objects.all()
    return render(request, 'main/main.html', {'posts': posts, 'all_posts': all_posts})


def open_post(request, post_slug):

    post = Post.objects.get(slug=post_slug)
    tags = post.tags.all()
    related_posts = Post.objects.filter(tags__tag__in=post.get_tags()).exclude(slug=post_slug).distinct()
    comments = post.comments.filter(post=post.pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            return redirect('open', post_slug=post.slug)
    else:
        form = CommentForm()
    contents = {'post': post,
                'related': related_posts,
                'tagss': tags,
                'form': form,
                'comments': comments}

    return render(request, 'main/post.html', contents)


def about(request):
    return render(request, 'main/author.html')


def search(request):
    query = request.GET.get('query')

    if query:
        results = Post.objects.filter(title__icontains=query)  # Assuming title field is to be searched
        context = {'query': query, 'posts': results, 'title': 'Results For'}
        return render(request, 'main/search.html', context)
    else:
        return redirect('home')


def search_by_tag(request, tag_slug):
    tag = Tag.objects.get(slug=tag_slug)
    posts = tag.get_posts()
    return render(request, 'main/search.html', {'query': tag, 'posts': posts, 'title': 'Results For'})


def categories(request):
    category = Category.objects.all()
    return render(request, 'secondary/categories.html', {'category': category})


def search_by_category(request, category_slug):
    cat = Category.objects.get(slug=category_slug)
    posts = cat.get_posts()
    return render(request, 'main/author.html', {'posts': posts, 'category': cat.category, 'desc': cat.description})
