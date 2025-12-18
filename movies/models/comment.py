
from django.conf import settings
from django.db import models
from django.db.models import ForeignKey, CASCADE

from movies.models.movie import Movie


class Comment(models.Model):
    user = ForeignKey(settings.AUTH_USER_MODEL,
                      on_delete=CASCADE,
                      related_name="comments")
    text = models.TextField()
    movie = ForeignKey(Movie, related_name="comments", on_delete=CASCADE)

    def __str__(self):
        return f"{self.user} - text '{self.text}' on {self.movie}"