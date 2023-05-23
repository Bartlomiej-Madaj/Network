from django.core.paginator import Paginator

def pagination(request, posts, num_of_pages):
    paginator = Paginator(posts, num_of_pages)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def select_post(posts):
    new_posts = list()
    for post in posts:
        comments = list()
        for comment in post.commented_post.all().order_by('-date'):
            new_comment = {
                "author": comment.author,
                "image": comment.author.image.url,
                "id": comment.id,
                "date": comment.date,
                "content": comment.content,
                "likes": comment.liked_comment.filter(is_active=True).count(),
                "like_authors": [comment_author.author for comment_author in comment.liked_comment.filter(is_active=True)]
            }
            comments.append(new_comment)
        new_post = {"author": post.author,
                    "image": post.author.image.url,
                    "id": post.id,
                    "likes": post.liked_post.filter(is_active=True).count(),
                    "like_authors": [post_author.author for post_author in post.liked_post.filter(is_active=True)],
                    "date": post.date,
                    "content": post.content,
                    "comments": comments,
                    }
        new_posts.append(new_post)
    return new_posts