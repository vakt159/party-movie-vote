from random import choice

from django.db.models import Count
from django.views.generic import DetailView
from movies.models import MovieSession, Vote, Movie


class MovieSessionDetailView(DetailView):
    model = MovieSession
    template_name = "movies/movie_session/movie_session_detail.html"
    context_object_name = "movie_session"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["winner"] = Movie.objects.get(id=context["movie_session"].movie_id)
        return context
