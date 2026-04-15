# blog/services/comment_service.py

from apps.blog.models import Comment, Post


def create_comment(*, post: Post, user=None, body: str) -> Comment:
    return Comment.objects.create(
        post=post,
        user=user,
        body=body
    )


def delete_comment(comment: Comment) -> None:
    comment.delete()


def get_comments_for_post(post: Post):
    return Comment.objects.filter(post=post)


def get_comment_by_id(comment_id):
    return Comment.objects.filter(id=comment_id).first()