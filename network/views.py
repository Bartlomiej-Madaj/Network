from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
import json
import requests
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .forms import NetworkForm
from django.utils.datastructures import MultiValueDictKeyError
import re
import secrets
import datetime 
import pytz
from django.utils import timezone

from .utils import select_post, pagination

from .models import User, Post, Comment, Post_like, Comment_like, Follower, ServicesUser

def index(request):
    posts_from_db = Post.objects.all().order_by('-date')
    posts = select_post(posts_from_db)
    page_obj = pagination(request, posts, num_of_pages=5)
    return render(request, "network/index.html", {"page_obj": page_obj})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    form = NetworkForm()
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        submitted_form = NetworkForm(request.POST, request.FILES)

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })
        
        if not submitted_form.is_valid():
            return render(request, "network/register.html", {"form": submitted_form})
        
        try:
            user_image = request.FILES['user_image']
        except MultiValueDictKeyError:
            user_image = 'images/default-avatar-profile.jpg'

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password, image=user_image)
            user.save()
            
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html", {"form": form})


def post(request):
    if request.method == "POST":
        new_post = request.POST['new_post']
        if not new_post.strip():
            messages.error(
                request, "Please, add some content into your post!", extra_tags="post_error")
            return HttpResponseRedirect(reverse('index'))
        user = request.user
        Post.objects.create(author=user, content=new_post)
        return HttpResponseRedirect(reverse('index'))

    return render(request, "network/404.html", {"message": "This page does not exist!!"})


def user(request, user_id):
    users_id = User.objects.all().values_list('id', flat=True)

    if user_id in users_id:
        user = User.objects.get(id=user_id)
        posts_from_db = Post.objects.order_by('-date').filter(author=user)
        posts = select_post(posts_from_db)
        page_obj = pagination(request, posts, num_of_pages=5)
        try:
            following_users = Follower.objects.get(user=user)
            followings = following_users.followers.all().count()
        except Follower.DoesNotExist:
            followings = 0

        try:
            follower_users = Follower.objects.get(
                user=request.user).followers.all()
        except Follower.DoesNotExist:
            follower_users = 0

        followers = user.followers_list.all().count()

        return render(request, 'network/profile.html', {"followings": followings, "followers": followers, "following_users": follower_users, "page_obj": page_obj, "watched_user": user})
    return render(request, "network/404.html", {"message": "This page does not exist!!"})


@csrf_exempt
def favorite(request):
    if request.method == 'POST':
        user = request.user
        user_id = json.loads(request.body).get('user_id')
        post_id = json.loads(request.body).get('post_id')
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found."}, status=404)

        try:
            post_like = Post_like.objects.get(author=user, post=post)
        except Post_like.DoesNotExist:
            post_like = None

        if user.id == int(user_id) and post.id == int(post_id) and not post_like:
            Post_like.objects.create(author=user, post=post, is_active=True)
            return JsonResponse({"redirect_url": reverse('index')})
        elif user.id == int(user_id) and post.id == int(post_id) and post_like.is_active:
            Post_like.objects.filter(
                author=user, post=post).update(is_active=False)
            return JsonResponse({"redirect_url": reverse('index')})
        elif user.id == int(user_id) and post.id == int(post_id) and not post_like.is_active:
            Post_like.objects.filter(
                author=user, post=post).update(is_active=True)
            return JsonResponse({"redirect_url": reverse('index')})
        else:
            return JsonResponse({"error": "Post or user not found."}, status=404)

    return render(request, "network/404.html", {"message": "This page does not exist!!"})


@csrf_exempt
def favorite_comment(request):
    if request.method == 'POST':
        user = request.user
        user_id = json.loads(request.body).get('user_id')
        post_id = json.loads(request.body).get('post_id')
        comment_id = json.loads(request.body).get('comment_id')
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            post = None

        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            comment = None

        try:
            comment_like = Comment_like.objects.get(
                author=user, comment=comment)
        except Comment_like.DoesNotExist:
            comment_like = None
        if comment.post != post:
            return JsonResponse({"error": "Comment not found."}, status=404)
        elif user.id == int(user_id) and comment.id == int(comment_id) and not comment_like:
            Comment_like.objects.create(
                author=user, comment=comment, is_active=True)
            return JsonResponse({"redirect_url": reverse('index')})
        elif user.id == int(user_id) and comment.id == int(comment_id) and comment_like.is_active:
            Comment_like.objects.filter(
                author=user, comment=comment).update(is_active=False)
            return JsonResponse({"redirect_url": reverse('index')})
        elif user.id == int(user_id) and comment.id == int(comment_id) and not comment_like.is_active:
            Comment_like.objects.filter(
                author=user, comment=comment).update(is_active=True)
            return JsonResponse({"redirect_url": reverse('index')})
        else:
            return JsonResponse({"error": "Comment not found."}, status=404)
    return render(request, "network/404.html", {"message": "This page does not exist!!"})


@csrf_exempt
def follow(request):
    if request.method == 'POST':
        user = request.user
        user_id = json.loads(request.body).get('user_id')
        users = User.objects.all().values_list('id', flat=True)
        if int(user_id) in users and int(user_id) != user.id:
            followed_user = User.objects.get(id=user_id)
            follower = Follower.objects.get_or_create(user=user)[0]
            if followed_user in follower.followers.all():
                follower.followers.remove(followed_user)
                return JsonResponse({"redirect_url": reverse('user_page', kwargs={"user_id": int(user_id)})})
            else:
                follower.followers.add(followed_user)
                return JsonResponse({"redirect_url": reverse('user_page', kwargs={"user_id": int(user_id)})})
        return JsonResponse({"error": "User not fonud!"}, status=404)

    return render(request, "network/404.html", {"message": "This page does not exist!!"})


@login_required
def following_posts(request):
    try:
        followers = Follower.objects.filter(user=request.user)[0].followers.all()
        posts_from_db = Post.objects.filter(author__in=followers).order_by('-date')
    except IndexError:
        posts_from_db = []
    posts = select_post(posts_from_db)
    page_obj = pagination(request, posts, num_of_pages=5)
    return render(request, "network/following.html", {"page_obj": page_obj})


@login_required
@csrf_exempt
def edit_post(request, post_id):
    if request.method == 'PATCH':
        entered_post_id = json.loads(request.body).get('id')
        entered_content = json.loads(request.body).get('content')
        try:
            post = Post.objects.filter(id=entered_post_id, author=request.user)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found."}, status=404)
        if int(entered_post_id) == post_id and entered_content.strip():
            post.update(content=entered_content)
            return JsonResponse({"redirect_url": reverse('index')})
        else:
            return JsonResponse({"error": "Post not found."}, status=404)

    try:
        post = Post.objects.get(id=post_id, author=request.user)
    except Post.DoesNotExist:
        return render(request, "network/404.html", {"message": "This page does not exist!!"})

    return render(request, 'network/edit_post.html', {"post": post})

@csrf_exempt
def comment_post(request):
    if request.method == "POST":
        comment_post = json.loads(request.body).get('content')
        post_id = json.loads(request.body).get('post_id')
        user = request.user
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return render(request, "network/404.html", {"message": "This page does not exist!!"})
        
        if not comment_post.strip():
            return JsonResponse({"message": "Add some comment!"})
        
        Comment.objects.create(author=user, post=post, content=comment_post)
        return JsonResponse({"redirect_url": reverse('index')})
    
    return render(request, "network/404.html", {"message": "This page does not exist!!"})


def auth_user(request, service):
    # A login token sent by the service
    try:
        service_token =service.split('=')[1]
    except IndexError:
        service_token = None

    # Endpoint to the services API
    if service_token:
        endpoint = f"http://127.0.0.1:8000/api/authorization/{service.split('=')[1]}"
    else:
        return HttpResponseRedirect(reverse('index'))
    
    # Authorization token. Better keep it in environment variables.
    login_token = 'b0b11519c6bb934433339990759a0456a2924c6a'
    headers = {
        'Authorization': f"Bearer {login_token}"
    }

    get_response = requests.get(endpoint, headers=headers)
    if get_response.ok:
        # A user email form services API.
        email = json.loads(get_response.content).get('email', None)
        midnight = datetime.datetime.combine(datetime.datetime.today() + datetime.timedelta(days=1), datetime.time.min)

        # Get if exist or create new user and service_user.  
        try:
            user = User.objects.get(email=email)
            if not ServicesUser.objects.filter(user=user).exists():
                services_user = ServicesUser.objects.create(user=user, start_date=datetime.datetime.now(), is_active=True)
            if midnight.timestamp() - datetime.datetime.now().timestamp() <= 0:
                services_user.delete()
                ServicesUser.objects.create(user=user, start_date=datetime.datetime.now(), is_active=True)
        except User.DoesNotExist:
            user = User.objects.create_user(f"username_{email.split('@')[0]}_{int(datetime.datetime.now().timestamp())}", email, f"{secrets.token_hex(32)}")
            user.save()
            ServicesUser.objects.create(user=user, start_date=datetime.datetime.now(), is_active=True)

        login(request, user)
        response = HttpResponseRedirect(reverse('index'))
        response.set_cookie('services', 'services_cookie', max_age=(midnight - datetime.datetime.now()).seconds)
        return response
    
    return HttpResponseRedirect(reverse('login'))

def check_user_authentication(request):

    try:
        services_user = ServicesUser.objects.get(user=request.user)
    except:
        services_user = None

    services_cookie = request.COOKIES.get('services')

    # User will be deleted after the cookie expires.
    if services_user and not services_cookie:
        services_user.delete()
        logout(request)
        return HttpResponseRedirect(reverse('index'))
    # Check if user is services user
    elif services_cookie and services_cookie:
        return JsonResponse({"success": True, "message": "Services user"})
    
    return JsonResponse({"success": True, "message": "No services user"})