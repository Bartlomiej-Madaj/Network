from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    image = models.ImageField(upload_to="images", null=True, default="images/default-avatar-profile.jpg")


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return f"Author: {self.author}, content: {self.content}"

class Post_like(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="like_author")
    is_active = models.BooleanField(default=False) 
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="liked_post")
 
    def __str__(self):
        return f"author: {self.author}, post: {self.post}"

class Follower(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followed_user")
    followers = models.ManyToManyField(User, related_name="followers_list")

    def __str__(self):
        return f"user: {self.user}, followers: {self.followers}" 
    
class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenting_user")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="commented_post")
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Author: {self.author}, comment: {self.content}"

class Comment_like(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_like_author")
    is_active = models.BooleanField(default=False) 
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="liked_comment")
    date = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"Author: {self.author}, comment: {self.comment}"
    