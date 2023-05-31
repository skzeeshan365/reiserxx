import json
import os
import random
from datetime import datetime, timedelta

import requests
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from google.cloud import translate
from google.oauth2 import service_account

from djangoProject1 import settings
from .forms import CommentForm, ContactForm, SubscriberForm
from .models import Category, Subscriber
from .models import Post, Contact
from .models import Tag


# Create your views here.


def home(request):
    return render(request, 'main/main.html', {'current_menu': 1, 'page_title': "ReiserX"})


def load_tags(request):
    tags = Tag.objects.annotate(num_posts=Count('posts')).order_by('-num_posts')[:5]
    tag_list = [{'name': tag.tag, 'slug': tag.slug} for tag in tags]
    return JsonResponse({'tags': tag_list})


def load_more_posts(request):
    page = int(request.GET.get('page', 2))
    posts_per_page = 5

    posts_query = Post.objects.filter(draft=False).order_by('-timestamp')
    paginator = Paginator(posts_query, posts_per_page)

    try:
        loaded_posts = paginator.page(page)
    except Exception:
        return JsonResponse({'rendered_posts': '', 'has_next_page': False})

    # Calculate the number of ads to insert
    num_ads = len(loaded_posts) // 5

    # Generate a list of unique random indices to insert ads
    ad_indices = random.sample(range(1, len(loaded_posts) + num_ads), num_ads)

    # Create a list to store posts and ad placeholders
    combined_list = []
    for index, post in enumerate(loaded_posts):
        combined_list.append(post)
        if index + 1 in ad_indices:
            ad_placeholder = Post(is_ad=True)  # Create an ad placeholder object
            combined_list.append(ad_placeholder)

    rendered_posts = render_to_string('main/partials/postlist.html', {'all_posts': combined_list})

    has_next_page = loaded_posts.has_next()
    return JsonResponse({'rendered_posts': rendered_posts, 'has_next_page': has_next_page})


def open_post(request, user, post_slug):
    try:
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

        subscribed = False
        if request.session.get('subscriber_id'):
            subscribed = True
        contents = {'post': post,
                    'related': related_posts,
                    'tagss': tags,
                    'form': form,
                    'comments': comments,
                    'subscribed': subscribed,
                    'SITE_KEY': settings.RECAPTCHA_PUBLIC_KEY}

        return render(request, 'main/post.html', contents)
    except Post.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Requested resource does not exist'})


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
            message = json.loads(form.errors.as_json())
            print(message)
            return JsonResponse({'status': 'error', 'message': message['email'][0]['message']})
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
    query = request.GET.get('q')

    if query:
        results = Post.search_by_title(query=query)  # Assuming title field is to be searched
        context = {'query': query, 'posts': results, 'title': 'Results For', 'current_menu': 1, 'page_title': query}
        return render(request, 'main/search.html', context)
    else:
        return redirect('home')


def search_by_tag(request, tag_slug):
    tag = Tag.objects.get(slug=tag_slug)
    posts = tag.get_posts()
    return render(request, 'main/search.html',
                  {'query': tag, 'posts': posts, 'title': 'Results For', 'current_menu': 1, 'page_title': tag})


def categories(request):
    category = Category.objects.all()
    return render(request, 'main/categories.html', {'category': category, 'current_menu': 2, 'page_title': 'Category'})


def search_by_category(request, category_slug):
    cat = Category.objects.get(slug=category_slug)
    posts = cat.get_posts()
    return render(request, 'main/category.html',
                  {'posts': posts, 'category': cat.category, 'desc': cat.description, 'category_image': cat.image.url,
                   'current_menu': 2, 'page_title': cat})


def search_by_author(request, username):
    try:
        user = User.objects.get(username=username)
        posts = Post.get_posts_by_user(user)
        context = {'posts': posts, 'user': user, 'current_menu': 1, 'page_title': username}
        return render(request, 'main/author.html', context)
    except User.DoesNotExist:
        context = {'message': 'User does not exist.'}
        return render(request, 'main/author_404.html', context)


def about(request):
    return render(request, 'main/about.html',
                  {'title': "Blast off into the Exciting Universe of ReiserX!"})


def subscribe(request):
    if request.method == 'POST':
        form = SubscriberForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data.get('recaptcha_response')

            # Validate reCAPTCHA token
            recaptcha_url = 'https://www.google.com/recaptcha/api/siteverify'
            recaptcha_secret_key = settings.RECAPTCHA_PRIVATE_KEY
            data = {'secret': recaptcha_secret_key, 'response': token}
            response = requests.post(url=recaptcha_url, data=data)
            if response.ok:
                result = response.json()
                if result.get('success') and result.get('score', 0) >= 0.5:
                    # Accept form submission
                    subscriber = form.save()
                    request.session['subscriber_id'] = subscriber.id

                    # set the cookie expiration time to a year from now
                    expires_at = datetime.now() + timedelta(days=365)
                    request.session.set_expiry(expires_at.timestamp())

                    return JsonResponse(
                        {'status': 'success', 'message': 'Your email is feeling like a lost puppy in the '
                                                         'digital world. Give it a little love by clicking '
                                                         'that verification link in your inbox!'})
                else:
                    # Reject form submission
                    return JsonResponse({'status': 'error', 'message': 'Invalid reCAPTCHA. Please try again.'})
            else:
                # reCAPTCHA API error
                return JsonResponse({'status': 'error', 'message': 'reCAPTCHA API error. Please try again.'})
        else:
            message = json.loads(form.errors.as_json())
            return JsonResponse({'status': 'error', 'message': message['email'][0]['message']})
    else:
        form = SubscriberForm()

    title = "Let's talk about nothing, it's a short conversation."
    message = "Ready to join the exclusive club? Subscribe now for access to the latest and greatest content, " \
              "exciting updates, and more virtual high-fives than you can handle! 😉👊 "
    return render(request, 'main/subscribe.html', {'form': form,
                                                   'SITE_KEY': settings.RECAPTCHA_PUBLIC_KEY,
                                                   'title': title,
                                                   'message': message})


def verify_email(request, subscriber_id):
    subscriber = Subscriber.objects.get(id=subscriber_id)
    subscriber.verified = True
    subscriber.save()
    messages.success(request, 'Your subscription has been verified. Thank you!')
    return render(request, 'main/email_verification.html',
                  {'message': "Congratulations, your email has passed the vibe check!",
                   'title': 'Email verified'
                   })


def lang(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        token = data.get('token')
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': settings.RECAPTCHA_PRIVATE_KEY,
                'response': token
            }
        )

        result = response.json()
        if not result.get('success') or result.get('score', 0) < 0.7:
            # Handle the reCAPTCHA verification failure
            return JsonResponse({'success': False, 'message': 'reCAPTCHA verification failed. Please try again later.'})
        else:
            # calling up google vision json file
            with open(r"main/key.json") as f:
                credentials_info = json.load(f)
            credentials = service_account.Credentials.from_service_account_info(credentials_info)

            # Initialize the Google Cloud Translation API client
            client = translate.TranslationServiceClient(credentials=credentials)

            # Call the API to retrieve the list of supported languages
            response = client.get_supported_languages(parent='projects/' + os.getenv('project_id'),
                                                      display_language_code="en")

            # Create a list of dictionaries containing language code, name, and native name
            language_list = []
            for language in response.languages:
                language_list.append({
                    'code': language.language_code,
                    'name': language.display_name,
                })

            # Return the language list as a JSON response
            return JsonResponse({'success': True, 'languages': language_list})
    else:
        raise Http404('Page not found')


def translate_post(request, user, post_slug, code):
    post = Post.objects.get(slug=post_slug).translate(code)
    tag = post.tags.all()
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

    subscribed = False
    if request.session.get('subscriber_id'):
        subscribed = True
    contents = {'post': post,
                'related': related_posts,
                'tagss': tag,
                'form': form,
                'comments': comments,
                'subscribed': subscribed}

    return render(request, 'main/post.html', contents)


def policy(request):
    return render(request, 'main/privacy_policy.html')