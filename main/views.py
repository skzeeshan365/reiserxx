import json
import random
from datetime import datetime, timedelta

import requests
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.sitemaps.views import sitemap
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from djangoProject1 import settings
from . import utils
from .forms import CommentForm, ContactForm, SubscriberForm, StableDiffusionForm, TagModelForm, WhisperModelForm
from .models import Category, Subscriber, Comment, Reply, Summary, TranslatedPost, PostLink
from .models import Post, Contact
from .models import Tag
from .sitemap_lang import DynamicSitemap
from .utils import generate_tags, summarize, gpt_neo_2_7_B, SUPPORTED_LANGUAGES, language_list, generate_image, whisper, \
    translation_threshold


def home(request):
    return render(request, 'main/Primary/main.html', {'current_menu': 1, 'page_title': "Home - ReiserX"})


def load_tags(request):
    tags = Tag.objects.annotate(num_posts=Count('posts')).order_by('-num_posts')[:5]
    tag_list = [{'name': tag.tag[0].upper() + tag.tag[1:], 'slug': tag.slug} for tag in tags]
    return JsonResponse({'tags': tag_list})


def load_categories(request):
    category = Category.objects.annotate(num_posts=Count('posts')).order_by('-num_posts')[:5]
    category_list = [{'name': category.category, 'slug': category.slug} for category in category]
    return JsonResponse({'categories': category_list})


def load_more_posts(request):
    page = int(request.GET.get('page', 2))
    posts_per_page = 5

    posts_query = Post.objects.filter(draft=False).order_by('-timestamp_modified', '-id')
    paginator = Paginator(posts_query, posts_per_page)

    try:
        loaded_posts = paginator.page(page)
    except Exception:
        return JsonResponse({'rendered_posts': '', 'has_next_page': False})

    # Calculate the number of ads to insert
    num_ads = len(loaded_posts) // 3

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
    post = get_object_or_404(Post, slug=post_slug)
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
                'SITE_KEY': settings.RECAPTCHA_PUBLIC_KEY,
                'code': 'en'}

    return render(request, 'main/Primary/post.html', contents)


def open_shared_post(request, short_slug):
    post = get_object_or_404(PostLink, short_slug=short_slug)
    return redirect('open', user=post.post.author, post_slug=post.post.slug)


def post_reply(request, comment_id):
    if request.method == 'POST':
        request_data = json.loads(request.body)  # Parse the JSON data
        reply_content = request_data.get('content')
        comment = Comment.objects.get(pk=comment_id)

        # Save the reply to the database
        Reply.objects.create(
            comment=comment,
            content=reply_content,
            user=request.user
        )

        subject = f"{request.user.username} has replied to your comment"

        message = render_to_string('main/About/email_template.html', {
            'recipient_name': comment.name,
            'sender_name': request.user.username,
            'comment_content': comment.content,
            'post_title': comment.post.title,
            'post_url': comment.post.get_absolute_post_url(request),
            'reply_content': reply_content,
        })

        to_email = comment.email
        utils.send_email(subject=subject, message=message, to_email=to_email)

        return JsonResponse({'message': 'Reply posted successfully.'})
    else:
        return JsonResponse({'message': 'Invalid request.'}, status=400)


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
    return render(request, 'main/About/contact.html', {'form': form,
                                                       'SITE_KEY': settings.RECAPTCHA_PUBLIC_KEY,
                                                       'title': title,
                                                       'message': message})


def search(request):
    query = request.GET.get('q')

    if query:
        results = Post.search_by_title(query=query)  # Assuming title field is to be searched
        context = {'query': query, 'posts': results, 'title': 'Results For', 'current_menu': 1, 'page_title': query}
        return render(request, 'main/Primary/search.html', context)
    else:
        return redirect('home')


def search_by_tag(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = tag.get_posts()
    return render(request, 'main/Primary/search.html',
                  {'query': tag, 'posts': posts, 'title': 'Results For', 'current_menu': 1, 'page_title': tag})


def categories(request):
    category = Category.objects.all()
    return render(request, 'main/Category/categories.html',
                  {'category': category, 'current_menu': 2, 'page_title': 'Category'})


def search_by_category(request, category_slug):
    cat = get_object_or_404(Category, slug=category_slug)
    posts = cat.get_posts()
    return render(request, 'main/Category/category.html',
                  {'posts': posts, 'category': cat.category, 'desc': cat.description, 'category_image': cat.image.url,
                   'current_menu': 2, 'page_title': cat})


def search_by_author(request, username):
    try:
        user = User.objects.get(username=username)
        posts = Post.get_posts_by_user(user)
        context = {'posts': posts, 'user': user, 'current_menu': 1, 'page_title': username}
        return render(request, 'main/Author/author.html', context)
    except User.DoesNotExist:
        context = {'message': 'User does not exist.'}
        return render(request, 'main/Author/author_404.html', context)


def about(request):
    return render(request, 'main/About/about.html')


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
    return render(request, 'main/Subscribe/subscribe.html', {'form': form,
                                                             'SITE_KEY': settings.RECAPTCHA_PUBLIC_KEY,
                                                             'title': title,
                                                             'message': message})


def verify_email(request, subscriber_id):
    subscriber = Subscriber.objects.get(id=subscriber_id)
    subscriber.verified = True
    subscriber.save()
    messages.success(request, 'Your subscription has been verified. Thank you!')
    return render(request, 'main/Subscribe/email_verification.html',
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
            # Create a list of dictionaries containing language code, name, and native name
            return JsonResponse({'success': True, 'languages': language_list})
    else:
        raise Http404('Page not found')


def translate_post(request, user, post_slug, code):
    if code in SUPPORTED_LANGUAGES:
        post = get_object_or_404(Post, slug=post_slug)

        total_text_length = len(post.title) + len(post.description) + len(post.content)
        if total_text_length > translation_threshold:
            return HttpResponse("Text is too long for translation.")
        post = post.translate(code=code)
    else:
        raise Http404
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
                'subscribed': subscribed,
                'SITE_KEY': settings.RECAPTCHA_PUBLIC_KEY,
                'code': code}

    return render(request, 'main/Primary/post.html', contents)


def policy(request):
    return render(request, 'main/About/privacy_policy.html')


def terms(request):
    return render(request, 'main/About/terms.html')


def refund(request):
    return render(request, 'main/About/refund_policy.html')


def stable_diffusion(request):
    if request.method == 'POST':
        form = StableDiffusionForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data.get('recaptcha_response')

            # Validate reCAPTCHA token
            recaptcha_url = 'https://www.google.com/recaptcha/api/siteverify'
            recaptcha_secret_key = settings.RECAPTCHA_PRIVATE_KEY
            data = {'secret': recaptcha_secret_key, 'response': token}
            response = requests.post(url=recaptcha_url, data=data)
            if response.ok:
                result = response.json()
                if result.get('success') and result.get('score', 0) >= 0.8:
                    # Accept form submission
                    input_text = form.cleaned_data['input_text']
                    try:
                        image = generate_image(input_text)
                        return JsonResponse(
                            {'status': 'success', 'message': 'Image generated', 'image': image,
                             'input_text': input_text})
                    except Exception as e:
                        return JsonResponse({'status': 'error', 'message': 'Service unavailable, please try again later'})

                else:
                    # Reject form submission
                    return JsonResponse({'status': 'error', 'message': 'Invalid reCAPTCHA. Please try again.'})
            else:
                # reCAPTCHA API error
                return JsonResponse({'status': 'error', 'message': 'reCAPTCHA API error. Please try again.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid prompt'})
    else:
        form = StableDiffusionForm()
        return render(request, 'main/AI/stable_diffusion.html',
                      {'form': form, 'SITE_KEY': settings.RECAPTCHA_PUBLIC_KEY, })


def tag_generation(request):
    if request.method == 'POST':
        form = TagModelForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data.get('recaptcha_response')

            # Validate reCAPTCHA token
            recaptcha_url = 'https://www.google.com/recaptcha/api/siteverify'
            recaptcha_secret_key = settings.RECAPTCHA_PRIVATE_KEY
            data = {'secret': recaptcha_secret_key, 'response': token}
            response = requests.post(url=recaptcha_url, data=data)
            if response.ok:
                result = response.json()
                if result.get('success') and result.get('score', 0) >= 0.8:
                    # Accept form submission
                    input_text = form.cleaned_data['input_text']
                    try:
                        tags = generate_tags(input_text)
                        return JsonResponse(
                            {'status': 'success', 'message': 'Tags generated', 'tags': tags,
                             'input_text': input_text})
                    except Exception as e:
                        return JsonResponse({'status': 'error', 'message': 'Service unavailable, please try again later'})

                else:
                    # Reject form submission
                    return JsonResponse({'status': 'error', 'message': 'Invalid reCAPTCHA. Please try again.'})
            else:
                # reCAPTCHA API error
                return JsonResponse({'status': 'error', 'message': 'reCAPTCHA API error. Please try again.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid prompt'})
    else:
        form = TagModelForm()
        return render(request, 'main/AI/tag_generation.html',
                      {'form': form, 'SITE_KEY': settings.RECAPTCHA_PUBLIC_KEY, })


def summarize_text(request):
    if request.method == 'POST':
        form = TagModelForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data.get('recaptcha_response')

            # Validate reCAPTCHA token
            recaptcha_url = 'https://www.google.com/recaptcha/api/siteverify'
            recaptcha_secret_key = settings.RECAPTCHA_PRIVATE_KEY
            data = {'secret': recaptcha_secret_key, 'response': token}
            response = requests.post(url=recaptcha_url, data=data)
            if response.ok:
                result = response.json()
                if result.get('success') and result.get('score', 0) >= 0.8:
                    # Accept form submission
                    input_text = form.cleaned_data['input_text']
                    try:
                        summary = summarize(input_text)
                        return JsonResponse(
                            {'status': 'success', 'message': 'Summary generated', 'summary': summary,
                             'input_text': input_text})
                    except Exception as e:
                        return JsonResponse({'status': 'error', 'message': 'Service unavailable, please try again later'})

                else:
                    # Reject form submission
                    return JsonResponse({'status': 'error', 'message': 'Invalid reCAPTCHA. Please try again.'})
            else:
                # reCAPTCHA API error
                return JsonResponse({'status': 'error', 'message': 'reCAPTCHA API error. Please try again.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid prompt'})
    else:
        form = TagModelForm()
        return render(request, 'main/AI/summary_generation.html',
                      {'form': form, 'SITE_KEY': settings.RECAPTCHA_PUBLIC_KEY, })


def transcribe(request):
    if request.method == 'POST':
        form = WhisperModelForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data.get('recaptcha_response')

            # Validate reCAPTCHA token
            recaptcha_url = 'https://www.google.com/recaptcha/api/siteverify'
            recaptcha_secret_key = settings.RECAPTCHA_PRIVATE_KEY
            data = {'secret': recaptcha_secret_key, 'response': token}
            response = requests.post(url=recaptcha_url, data=data)
            if response.ok:
                result = response.json()
                if result.get('success') and result.get('score', 0) >= 0.8:
                    # Accept form submission
                    input_text = form.cleaned_data['input_text']
                    try:
                        transcription = whisper(input_text)
                        return JsonResponse(
                            {'status': 'success', 'message': 'Text generated', 'transcription': transcription,
                             'input_text': input_text})
                    except Exception as e:
                        return JsonResponse({'status': 'error', 'message': 'Service unavailable, please try again later'})
                else:
                    # Reject form submission
                    return JsonResponse({'status': 'error', 'message': 'Invalid reCAPTCHA. Please try again.'})
            else:
                # reCAPTCHA API error
                return JsonResponse({'status': 'error', 'message': 'reCAPTCHA API error. Please try again.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid prompt'})
    else:
        form = WhisperModelForm()
        return render(request, 'main/AI/transcription.html',
                      {'form': form, 'SITE_KEY': settings.RECAPTCHA_PUBLIC_KEY, })


def summarize_text_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        if 'input_text' in data and 'recaptcha_response' in data:
            input_text = data.get('input_text')
            token = data.get('recaptcha_response')
            slug = data.get('slug')

            # Validate reCAPTCHA token
            recaptcha_url = 'https://www.google.com/recaptcha/api/siteverify'
            recaptcha_secret_key = settings.RECAPTCHA_PRIVATE_KEY
            data = {'secret': recaptcha_secret_key, 'response': token}
            response = requests.post(url=recaptcha_url, data=data)
            if response.ok:
                result = response.json()
                if result.get('success') and result.get('score', 0) >= 0.7:
                    # Accept form submission
                    try:
                        summary = summarize(input_text)
                        post = Post.objects.get(slug=slug)
                        summary_model = Summary(
                            post=post,
                            summary=summary[0],
                        )
                        summary_model.save()
                        return JsonResponse(
                            {'status': 'success', 'message': 'Summary generated', 'summary': summary})
                    except Exception as e:
                        return JsonResponse(
                            {'status': 'error', 'message': 'Service unavailable, please try again later'})
                else:
                    # Reject api call
                    return JsonResponse({'status': 'error', 'message': 'Invalid reCAPTCHA. Please try again.'})
            else:
                # reCAPTCHA API error
                return JsonResponse({'status': 'error', 'message': 'reCAPTCHA API error. Please try again.'})
        JsonResponse({'status': 'error', 'message': 'reCAPTCHA API error. Please try again.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def generation_gpt_neo_2_7_B(request):
    if request.method == 'POST':
        form = TagModelForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data.get('recaptcha_response')

            # Validate reCAPTCHA token
            recaptcha_url = 'https://www.google.com/recaptcha/api/siteverify'
            recaptcha_secret_key = settings.RECAPTCHA_PRIVATE_KEY
            data = {'secret': recaptcha_secret_key, 'response': token}
            response = requests.post(url=recaptcha_url, data=data)
            if response.ok:
                result = response.json()
                if result.get('success') and result.get('score', 0) >= 0.9:
                    # Accept form submission
                    input_text = form.cleaned_data['input_text']
                    try:
                        generation = gpt_neo_2_7_B(input_text)
                        return JsonResponse(
                            {'status': 'success', 'message': 'Text generated', 'generation': generation,
                             'input_text': input_text})
                    except Exception as e:
                        return JsonResponse({'status': 'error', 'message': 'Service unavailable, please try again later'})

                else:
                    # Reject form submission
                    return JsonResponse({'status': 'error', 'message': 'Invalid reCAPTCHA. Please try again.'})
            else:
                # reCAPTCHA API error
                return JsonResponse({'status': 'error', 'message': 'reCAPTCHA API error. Please try again.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid prompt'})
    else:
        form = TagModelForm()
        return render(request, 'main/AI/text_generation_gpt-neo.html',
                      {'form': form, 'SITE_KEY': settings.RECAPTCHA_PUBLIC_KEY, })


def dynamic_sitemap(request, language):
    if language not in SUPPORTED_LANGUAGES:
        # Handle unsupported languages here, e.g., return a 404 response
        return HttpResponse(status=404)

    # Create a dictionary to hold sitemap instances for different languages
    sitemap_instances = {
        f'posts_{language}': DynamicSitemap(language),
    }

    # Generate the sitemap for the specified language
    return sitemap(request, sitemaps=sitemap_instances)


def sitemap_index(request):
    # Create a list of sitemap URLs for each language
    sitemap_urls = []
    for language in SUPPORTED_LANGUAGES:
        url = f"https://reiserx.com/sitemap-posts-{language}.xml"
        sitemap_urls.append(url)

    # Load the sitemap index template and render it with the sitemap URLs
    template = loader.get_template('sitemap_index.xml')
    context = {'sitemap_urls': sitemap_urls}
    sitemap_index_xml = template.render(context)

    # Return the sitemap index XML as an HttpResponse
    return HttpResponse(sitemap_index_xml, content_type='application/xml')


def lang_page(request):
    return render(request, 'main/Languages/languages.html', {'languages': language_list, 'current_menu': 1, 'page_title': f"Languages - ReiserX"})


def lang_posts_page(request, code):
    language_dict = {language['code']: language for language in language_list}
    name = language_dict[code]['name']
    return render(request, 'main/Languages/posts.html', {'current_menu': 1, 'page_title': f"Home - {name} - ReiserX", 'code': code, 'name': name})


def load_lang_posts(request, code):
    page = int(request.GET.get('page', 2))
    posts_per_page = 5

    posts_query = TranslatedPost.objects.filter(language_code=code).order_by('-id')
    paginator = Paginator(posts_query, posts_per_page)

    try:
        loaded_posts = paginator.page(page)
    except Exception:
        return JsonResponse({'rendered_posts': '', 'has_next_page': False})

    num_ads = len(loaded_posts) // 3

    ad_indices = random.sample(range(1, len(loaded_posts) + num_ads), num_ads)

    combined_list = []
    for index, post in enumerate(loaded_posts):
        combined_list.append(post)
        if index + 1 in ad_indices:
            post = TranslatedPost()
            post.is_ad = True
            ad_placeholder = post  # Create an ad placeholder object
            combined_list.append(ad_placeholder)

    rendered_posts = render_to_string('main/partials/postlist_lang.html', {'all_posts': loaded_posts})

    has_next_page = loaded_posts.has_next()

    return JsonResponse({'rendered_posts': rendered_posts, 'has_next_page': has_next_page})


def screenshot_policy(request):
    return render(request, 'secondary/screenshot_policy.html')


def message_name(request, name):
    user_ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if user_ip:
        user_ip = user_ip.split(',')[0].strip()
    else:
        user_ip = request.META.get('REMOTE_ADDR')

    try:
        response = requests.get(f'https://ipinfo.io/{user_ip}?token=71eb0bb6b672d2')
        data = response.json()

        country = data.get('country', 'Unknown')
        state = data.get('region', 'Unknown')
        city = data.get('city', 'Unknown')
        postal_code = data.get('postal', 'Unknown')

        subject = "Message opened"
        message = f"""\
                    <html>
                    <body>
                        <p>{name} has opened,</p>
                        <p>IP Address: {user_ip}</p>
                        <p>Country: {country}</p>
                        <p>State: {state}</p>
                        <p>City: {city}</p>
                        <p>Postal code: {postal_code}</p>
                    </body>
                    </html>
                """

        to_email = 'skzeeshan3650@gmail.com'

        utils.send_email(subject=subject, message=message, to_email=to_email)
    except Exception as e:
        pass
    return render(request, 'secondary/Test/messsage_name.html', {'name': name})