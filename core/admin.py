from django.contrib import admin
from .models import Profile, Post, LikePosts, FollowersCount, Notification, Comment

admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(LikePosts)
admin.site.register(FollowersCount)
admin.site.register(Notification)
admin.site.register(Comment)