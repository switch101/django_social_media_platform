from random import shuffle
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from core.models import User, Post, LikePosts, FollowersCount, Notification, Comment, Conversation
from .models import Message
from itertools import chain
from .forms import CommentForm, ConversationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.models import Profile


@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))

    for post in feed_list:
        post.comments = list(reversed(Comment.objects.filter(post=post)))

    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)

    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if (x not in list(current_user))]
    shuffle(final_suggestions_list)
    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))

    comment_form = CommentForm()

    return render(request, 'index.html', {'user_profile': user_profile, 'posts': feed_list,
                                          'suggestions_username_profile_list': suggestions_username_profile_list[:4],
                                          'comment_form': comment_form})


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already taken!")
            return redirect('signup')
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken!")
            return redirect('signup')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()

            user_login = auth.authenticate(username=username, password=password)
            auth.login(request, user_login)
            # create a profile object for the new user
            user_model = User.objects.get(username=username)
            new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
            new_profile.save()
            return redirect('/')
    else:
        return render(request, "signup.html")


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, "Invalid username or password!")
            return redirect('signin')
    else:
        return render(request, "signin.html")


@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')


@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        if 'profile_picture' in request.FILES:
            user_profile.profile_img = request.FILES['profile_picture']

        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.save()
        user_profile.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user_profile.bio = request.POST.get('bio', '')
        user_profile.location = request.POST.get('location', '')
        user_profile.working_at = request.POST.get('working_at', '')
        user_profile.relationship = request.POST.get('relationship', '0')
        user_profile.save()

    return render(request, "setting.html", {'user_profile': user_profile})


@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES['image_upload']
        caption = request.POST.get('caption', '')

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()
        return redirect("index")
    else:
        return redirect('index')


@login_required(login_url='signin')
def like_post(request):
    if request.method == 'GET':
        username = request.user.username
        post_id = request.GET.get('post_id')
        post = Post.objects.get(id=post_id)
        likefilter = LikePosts.objects.filter(post_id=post_id, username=username).first()
        if likefilter is None:
            new_like = LikePosts.objects.create(post_id=post_id, username=username)
            new_like.save()

            post.no_of_likes += 1
            post.save()
            post_owner = post.user
            if isinstance(post_owner, User):
                Notification.objects.create(user=post_owner, notification_type='like', post=post)
            else:
                print("Post owner is not a User:", post_owner)

            return redirect("index")
        else:
            likefilter.delete()

            post.no_of_likes -= 1
            post.save()

            return redirect("index")


def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)

    # Fetch followers and following count
    user_followers = FollowersCount.objects.filter(user=pk).count()
    user_following = FollowersCount.objects.filter(follower=pk).count()

    # Fetch followers and following users
    followers = FollowersCount.objects.filter(user=pk)
    following = FollowersCount.objects.filter(follower=pk)

    # Get the list of followers and following users' usernames
    followers_list = [follower.follower for follower in followers]
    following_list = [followed_user.user for followed_user in following]

    # Retrieve user objects for followers and following
    followers_users = User.objects.filter(username__in=followers_list)
    following_users = User.objects.filter(username__in=following_list)

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'user_followers': user_followers,
        'user_following': user_following,
        'followers_users': followers_users,
        'following_users': following_users
    }

    # Fetch comments for each post
    for post in user_posts:
        post.comments = Comment.objects.filter(post=post)

    return render(request, 'profile.html', context)

    # Fetch comments for each post
    for post in user_posts:
        post.comments = Comment.objects.filter(post=post)

    return render(request, 'profile.html', context)


def follow(request):
    if request.method == 'GET':
        follower = request.GET.get('follower')
        user = request.GET.get('user')

        if follower is not None and user is not None:
            if FollowersCount.objects.filter(follower=follower, user=user).exists():
                delete_follower = FollowersCount.objects.get(follower=follower, user=user)
                delete_follower.delete()
            else:
                new_follower = FollowersCount.objects.create(follower=follower, user=user)
                new_follower.save()

                if user != follower:
                    Notification.objects.create(user=User.objects.get(username=user),
                                                notification_type='follower')

            return redirect("/profile/" + user)

    return redirect('/')


@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

        username_profile_list = list(chain(*username_profile_list))
    return render(request, 'search.html',
                  {'user_profile': user_profile, 'username_profile_list': username_profile_list})


@login_required(login_url='signin')
def notifications(request):
    notifications = Notification.objects.filter(user=request.user)

    return render(request, 'notifications.html', {'notifications': notifications})


def submit_comment(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        text = request.POST.get('text')
        user = request.user
        comment = Comment(post_id=post_id, user=user, comment_text=text)
        comment.save()

    return redirect('index')


def post_detailed_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = list(reversed(Comment.objects.filter(post=post)))
    return render(request, 'post_detailed_view.html', {'post': post, 'comments': comments})



def conversations(request):
    user = request.user
    conversations = user.conversations.all()
    return render(request, 'conversations.html', {'conversations': conversations})


def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    form = ConversationForm()
    followers = FollowersCount.objects.filter(user=request.user)

    if request.method == 'POST':
        form = ConversationForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            message = Message.objects.create(conversation=conversation, sender=request.user, content=content)
            return redirect('conversation_detail', conversation_id=conversation_id)

    return render(request, 'conversation_detail.html',
                  {'conversation': conversation, 'form': form, 'followers': followers})


def send_message(request, conversation_id):
    if request.method == 'POST':
        conversation = Conversation.objects.get(id=conversation_id)
        sender = request.user
        content = request.POST['content']
        message = Message.objects.create(conversation=conversation, sender=sender, content=content)
        return redirect('conversation_detail', conversation_id=conversation_id)


def conversations(request):
    followers = FollowersCount.objects.filter(follower=request.user.username)

    if request.method == 'POST':
        form = ConversationForm(request.POST)
        if form.is_valid():
            pass
    else:
        form = ConversationForm()

    return render(request, 'conversations.html', {'followers': followers, 'form': form})
