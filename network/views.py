from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
import json
from django.http import JsonResponse

from .models import User, Posts, Follow, Likes

def remove_like(request, post_id):
    post = Posts.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    Like = Likes.objects.filter(user=user, post=post)
    Like.delete()
    return JsonResponse({"message": "Like removed"})

def add_like(request, post_id):
    post = Posts.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    NewLike = Likes(user=user, post=post)
    NewLike.save()
    return JsonResponse({"message": "Like added"})

def index(request):
    posts = Posts.objects.all().order_by("id").reverse()

    # paginator

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts_of_page = paginator.get_page(page_number)

    allLikes = Likes.objects.all()

    whoYouLiked = []
    try:
        for like in allLikes:
            if like.user.id == request.user.id:
                whoYouLiked.append(like.post.id)
    except:
        whoYouLiked = []

    return render(request, "network/index.html", {
        "posts": posts,
        "posts_of_page": posts_of_page,
        "whoYouLiked": whoYouLiked,
    })

def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    posts = Posts.objects.filter(user=user).order_by("id").reverse()

    following = Follow.objects.filter(user_following=user)
    followers = Follow.objects.filter(user_followed=user)

    try:
        checkFollow = followers.filter(user_following=User.objects.get(pk=request.user.id))
        if len(checkFollow) != 0: 
            isFollowing = True
        else:
            isFollowing = False
    except:
        isFollowing = False

    # paginator

    paginator = Paginator(posts, 10)
    pageNumber = request.GET.get('page')
    posts_of_page = paginator.get_page(pageNumber)

    return render(request, "network/profile.html",{
        "posts": posts,
        "posts_of_page": posts_of_page,
        "username": user.username, 
        "following": following,
        "followers": followers,
        "isFollowing": isFollowing,
        "users_profile": user,
    })

def following(request):
    currentUser = User.objects.get(pk=request.user.id)
    peopleFollowing = Follow.objects.filter(user_following=currentUser)
    posts = Posts.objects.all().order_by("id").reverse()

    followingPosts = []

    for post in posts:
        for person in peopleFollowing:
            if person.user_followed == post.user:
                followingPosts.append(post)
    
    # paginator

    paginator = Paginator(followingPosts, 10)
    pageNumber = request.GET.get('page')
    posts_of_page = paginator.get_page(pageNumber)

    allLikes = Likes.objects.all()

    whoYouLiked = []
    try:
        for like in allLikes:
            if like.user.id == request.user.id:
                whoYouLiked.append(like.post.id)
    except:
        whoYouLiked = []

    return render(request, "network/following.html",{
        "posts_of_page": posts_of_page,
        "whoYouLiked": whoYouLiked,
    })
    

def follow(request):
    userfollow = request.POST['userfollow']
    currentUser = User.objects.get(pk=request.user.id)
    userfollowData = User.objects.get(username=userfollow)
    f = Follow(user_following=currentUser, user_followed=userfollowData)
    f.save()
    user_id = userfollowData.id 
    return HttpResponseRedirect(reverse(profile, kwargs={'user_id' : user_id}))

def unfollow(request):
    userfollow = request.POST['userfollow']
    currentUser = User.objects.get(pk=request.user.id)
    userfollowData = User.objects.get(username=userfollow)
    f = Follow.objects.get(user_following=currentUser, user_followed=userfollowData)
    f.delete()
    user_id = userfollowData.id 
    return HttpResponseRedirect(reverse(profile, kwargs={'user_id' : user_id}))


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
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

def new_post(request):
    if request.method == "POST":
        content = request.POST['post-content']
        user = User.objects.get(pk=request.user.id)
        post = Posts(content=content, user=user)
        post.save()
    return HttpResponseRedirect(reverse(index))

def edit(request, post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        edit_post = Posts.objects.get(pk=post_id)
        edit_post.content = data["content"]
        edit_post.save()
        return JsonResponse({"message": "Change successful", "data": data["content"]})

