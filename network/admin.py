from django.contrib import admin

from.models import User, Follower, Comment, Comment_like, Post_like, Post

# Register your models here.

admin.site.register(User)
admin.site.register(Follower)
admin.site.register(Comment)
admin.site.register(Comment_like)
admin.site.register(Post_like)
admin.site.register(Post)

