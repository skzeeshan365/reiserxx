from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .forms import CommentForm
from .models import Post
from .models import Tag
from .models import Category

# Create your views here.


def home(request):
    posts = Post.objects.order_by('-timestamp')[:2]
    all_posts = Post.objects.all()
    return render(request, 'main/main.html', {'posts': posts, 'all_posts': all_posts, 'current_menu': 1})


def open_post(request, user, post_slug):

    post = Post.objects.get(slug=post_slug)
    print(post.get_absolute_url())
    tags = post.tags.all()
    related_posts = post.get_related_posts()
    comments = post.get_comments()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            return redirect('open', user=user, post_slug=post.slug)
    else:
        form = CommentForm()
    contents = {'post': post,
                'related': related_posts,
                'tagss': tags,
                'form': form,
                'comments': comments}

    return render(request, 'main/post.html', contents)


def about(request):
    return render(request, 'main/category.html', {'current_menu': 3})


def search(request):
    query = request.GET.get('query')

    if query:
        results = Post.search_by_title(query=query)  # Assuming title field is to be searched
        context = {'query': query, 'posts': results, 'title': 'Results For', 'current_menu': 1}
        return render(request, 'main/search.html', context)
    else:
        return redirect('home')


def search_by_tag(request, tag_slug):
    tag = Tag.objects.get(slug=tag_slug)
    posts = tag.get_posts()
    return render(request, 'main/search.html', {'query': tag, 'posts': posts, 'title': 'Results For', 'current_menu': 1})


def categories(request):
    category = Category.objects.all()
    return render(request, 'main/categories.html', {'category': category, 'current_menu': 2})


def search_by_category(request, category_slug):
    cat = Category.objects.get(slug=category_slug)
    posts = cat.get_posts()
    return render(request, 'main/category.html', {'posts': posts, 'category': cat.category, 'desc': cat.description, 'current_menu': 2})


def search_by_author(request, username):
    user = User.objects.get(username=username)
    posts = Post.get_posts_by_user(user)
    context = {'posts': posts, 'user': user, 'current_menu': 1}
    return render(request, 'main/author.html', context)
