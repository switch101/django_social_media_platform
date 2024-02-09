from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
urlpatterns = [
    path("", views.index, name="index"),
    path("signup", views.signup, name="signup"),
    path("signin", views.signin, name="signin"),
    path("logout", views.logout, name="logout"),
    path("settings", views.settings, name="settings"),
    path("upload", views.upload, name="upload"),
    path("profile/<str:pk>", views.profile, name="profile"),
    path("like-post", views.like_post, name="like-post"),
    path("follow", views.follow, name="follow"),
    path("search", views.search, name="search"),
    path("submit_comment", views.submit_comment, name="submit_comment"),
    path('post/<uuid:post_id>/', views.post_detailed_view, name='post_detailed_view'),
    path("notifications", views.notifications, name="notifications"),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

