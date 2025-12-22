from django.conf import settings
from django.db import models
from django.db.models import ManyToManyField, OneToOneField, SET_NULL

from movies.models.movie import Movie
from movies.models.movie_session import MovieSession


class VoteSession(models.Model):
    name = models.CharField(max_length=255)
    members = ManyToManyField(settings.AUTH_USER_MODEL,
                              related_name="vote_sessions")
    movies = ManyToManyField(Movie, related_name="vote_sessions")
    movie_session = OneToOneField(MovieSession,
                                  related_name="vote_session",
                                  on_delete=SET_NULL, null=True)
    event_date_time = models.DateTimeField()

    class Meta:
        ordering = ["-event_date_time"]

    def __str__(self):
        return f"{self.name} at {self.event_date_time.strftime("%d-%m-%Y, %H:%M")}"