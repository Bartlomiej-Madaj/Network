
from django.urls import path


from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.post, name="post"),
    path("favorite", views.favorite, name="favorite"),
    path("favorite_comment", views.favorite_comment, name="favorite_comment"),
    path("follow", views.follow, name="follow"),
    path("following-posts", views.following_posts, name="following_posts"),
    path("comment_post", views.comment_post, name="comment_post"),
    path("check-user-authentication", views.check_user_authentication,),
    path("user/<int:user_id>", views.user, name="user_page"),
    path("edit/<int:post_id>", views.edit_post, name="edit"),
    path('<str:service>', views.auth_user),
] 
