import requests
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect

from djangoProject1 import settings
from .forms import CommentForm, ContactForm
from .models import Category
from .models import Post, Contact
from .models import Tag


# Create your views here.


def home(request):
    posts = Post.objects.order_by('-timestamp')[:4]
    all_posts = Post.objects.all()
    return render(request, 'main/main.html', {'posts': posts, 'all_posts': all_posts, 'current_menu': 1, 'page_title': "ReiserX"})


def open_post(request, user, post_slug):

    post = Post.objects.get(slug=post_slug)
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


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            message = form.cleaned_data.get('message')
            token = form.cleaned_data.get('recaptcha_response')

            # Validate reCAPTCHA token
            recaptcha_url = 'https://www.google.com/recaptcha/api/siteverify'
            recaptcha_secret_key = settings.RECAPTCHA_PRIVATE_KEY
            data = {'secret': recaptcha_secret_key, 'response': token}
            response = requests.post(url=recaptcha_url, data=data)
            print(response.json())
            if response.ok:
                result = response.json()
                if result.get('success') and result.get('score', 0) >= 0.5:
                    # Accept form submission
                    contacts = Contact(username=username, email=email, message=message)
                    contacts.save()
                    return JsonResponse({'status': 'success', 'message': 'Your message has been sent successfully.'})
                else:
                    # Reject form submission
                    return JsonResponse({'status': 'error', 'message': 'Invalid reCAPTCHA. Please try again.'})
            else:
                # reCAPTCHA API error
                return JsonResponse({'status': 'error', 'message': 'reCAPTCHA API error. Please try again.'})
        else:
            # Invalid form data
            return JsonResponse({'status': 'error', 'message': 'Invalid form data. Please try again.'})
    else:
        # GET request
        form = ContactForm()
    title = "Let's talk about everything."
    message = "Whether you have feedback, questions, or just want to say hello, we're here to listen and engage in " \
              "conversation. "
    return render(request, 'main/contact.html', {'form': form,
                                                 'SITE_KEY': settings.RECAPTCHA_PUBLIC_KEY,
                                                 'title': title,
                                                 'message': message})


def search(request):
    query = request.GET.get('search')

    if query:
        results = Post.search_by_title(query=query)  # Assuming title field is to be searched
        context = {'query': query, 'posts': results, 'title': 'Results For', 'current_menu': 1, 'page_title': query}
        return render(request, 'main/search.html', context)
    else:
        return redirect('home')


def search_by_tag(request, tag_slug):
    tag = Tag.objects.get(slug=tag_slug)
    posts = tag.get_posts()
    return render(request, 'main/search.html', {'query': tag, 'posts': posts, 'title': 'Results For', 'current_menu': 1, 'page_title': tag})


def categories(request):
    category = Category.objects.all()
    return render(request, 'main/categories.html', {'category': category, 'current_menu': 2, 'page_title': 'Category'})


def search_by_category(request, category_slug):
    cat = Category.objects.get(slug=category_slug)
    posts = cat.get_posts()
    return render(request, 'main/category.html', {'posts': posts, 'category': cat.category, 'desc': cat.description, 'current_menu': 2, 'page_title': cat})


def search_by_author(request, username):
    user = User.objects.get(username=username)
    posts = Post.get_posts_by_user(user)
    context = {'posts': posts, 'user': user, 'current_menu': 1, 'page_title': username}
    return render(request, 'main/author.html', context)


def about(request):
    content = """Welcome to the universe of ReiserX, where adventure and discovery await! Get ready to blast off on a cosmic journey like no other, filled with excitement, intrigue, and a healthy dose of humor.

At ReiserX, they're all about exploring the vast mysteries of the universe and having a blast while doing it. Their team of expert explorers will take you on a wild ride through the cosmos, sharing fascinating insights and discoveries along the way.

From the latest in cutting-edge technology to the weirdest and most bizarre scientific discoveries, ReiserX has got you covered. And they're not afraid to get a little quirky with their content either. Their team loves to sprinkle in jokes and humorous anecdotes, making learning fun and engaging.

Did you know that there's a planet where it rains diamonds? Or that there's a massive black hole in the center of our galaxy that's millions of times larger than our sun? These are just a couple of the amazing facts you'll discover as you journey through the universe with ReiserX.

So come join the fun and excitement of ReiserX, where the possibilities are endless and the adventure never ends. Get ready to blast off into a world of discovery and wonder, and who knows - maybe you'll even discover a new planet or two!"""
    return render(request, 'main/about.html', {'content': content, 'title': "Blast off into the Exciting Universe of ReiserX!"})