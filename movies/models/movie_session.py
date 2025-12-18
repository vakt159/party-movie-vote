from django.conf import settings
from django.db import models
from django.db.models import ManyToManyField, ForeignKey, SET_NULL

from movies.models.movie import Movie


class MovieSession(models.Model):
    name = models.CharField(max_length=255)
    members = ManyToManyField(settings.AUTH_USER_MODEL, related_name="movie_sessions")
    movie = ForeignKey(Movie, related_name="movie_sessions", on_delete=SET_NULL, null=True)
    event_date_time = models.DateTimeField()