from django.conf import settings
from django.db import models
from django.db.models import OneToOneField, CASCADE, ForeignKey

from movies.models.movie import Movie
from movies.models.vote_session import VoteSession


class Vote(models.Model):
    user = ForeignKey(settings.AUTH_USER_MODEL,
                      related_name="votes",
                      on_delete=CASCADE)
    movie = ForeignKey(Movie, related_name="votes", on_delete=CASCADE)
    vote_session = ForeignKey(VoteSession, related_name="votes",
                              on_delete=CASCADE)
