from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Posts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    content = models.CharField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post {self.id} by {self.user} on {self.timestamp.strftime('%d %b %Y %H : %M : %S')}"

class Follow(models.Model):
    user_following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    user_followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followed")

    def __str__(self):
        return f"{self.user_following} is following {self.user_followed}"

class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_like")
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name="post_like")

    def __str__(self):
        return f"{self.user} liked {self.post}"