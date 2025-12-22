from datetime import timedelta
from random import choice
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.db.models.aggregates import Count
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic
from django.views.generic import FormView

from movies.forms.add_movie_to_vote_session_form import \
    AddMovieToVoteSessionForm
from movies.forms.vote_session_create_form import VoteSessionCreateForm
from movies.models import VoteSession, Movie, Vote, MovieSession


class VoteSessionListView(LoginRequiredMixin, generic.ListView):
    model = VoteSession
    template_name = "movies/vote_session/vote_session_list.html"
    context_object_name = "vote_sessions"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        two_hours_ago = now + timedelta(hours=2)

        context["active_events"] = VoteSession.objects.filter(
            event_date_time__gt=two_hours_ago
        ).order_by("event_date_time")

        return context


class VoteSessionListPartialView(LoginRequiredMixin, generic.ListView):
    model = VoteSession
    template_name = "movies/vote_session/partial/vote_session_partial.html"
    context_object_name = "vote_sessions"

    def get_queryset(self):
        queryset = VoteSession.objects.all()
        if search := self.request.GET.get("search"):
            queryset = queryset.filter(
                name__icontains=search
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        now = timezone.now()
        two_hours_ago = now + timedelta(hours=2)

        context["active_events"] = VoteSession.objects.filter(
            event_date_time__gt=two_hours_ago
        ).order_by("event_date_time")
        return context


class AddMovieToVoteSessionView(LoginRequiredMixin, FormView):
    form_class = AddMovieToVoteSessionForm
    template_name = "movies/movie/add_to_vote_session.html"
    success_url = reverse_lazy("movies:movies-list")

    def dispatch(self, request, *args, **kwargs):
        self.movie = get_object_or_404(Movie, id=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["movie"] = self.movie
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context["form"]
        context["movie"] = self.movie
        context["has_available_sessions"] = form.fields[
            "vote_sessions"].queryset.exists()
        return context

    def form_valid(self, form):
        vote_sessions = form.cleaned_data["vote_sessions"]

        for vote_session in vote_sessions:
            vote_session.movies.add(self.movie)

        return super().form_valid(form)


@login_required
def vote_session_join(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden()
    vote_session = get_object_or_404(VoteSession, pk=pk)
    vote_session.members.add(request.user)
    vote_sessions = VoteSession.objects.all()
    active_events = VoteSession.objects.filter(
        event_date_time__gt=timezone.now())
    return render(
        request,
        "movies/vote_session/partial/vote_session_partial.html",
        {
            "vote_sessions": vote_sessions,
            "active_events": active_events,
            "user": request.user,
        }
    )

class VoteSessionDetailView(LoginRequiredMixin, generic.DetailView):
    model = VoteSession
    context_object_name = "vote_session"
    template_name = "movies/vote_session/vote_session_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vote_session = context["vote_session"]
        is_voted = True if Vote.objects.filter(
            vote_session=vote_session,
            user=self.request.user) else False
        context["is_voted"] = is_voted
        now = timezone.now()
        event_dt = vote_session.event_date_time
        substr = event_dt - now <= timedelta(hours=2)
        winner = (
            Vote.objects
            .filter(vote_session=vote_session)
            .values("movie__id", "movie__name")
            .annotate(votes_count=Count("id"))
            .order_by("-votes_count")
            .first()
        )
        if not winner:
            movies = vote_session.movies.all()
            random_movie = choice(list(movies))
            winner = {"movie__id": random_movie.id,
                          "movie__name": random_movie.name}

        movie_session = MovieSession.objects.filter(
            vote_session__id=vote_session.id)
        if substr:
            if movie_session:
                context["result"] = movie_session[0]
            else:
                movie_session = MovieSession.objects.create(
                    name=vote_session.name,
                    event_date_time=vote_session.event_date_time,
                    movie_id=winner.get("movie__id"),
                )
                movie_session.members.set(vote_session.members.all())
                vote_session.movie_session = movie_session
                vote_session.save()
                context["result"] = movie_session

        movies_with_votes = vote_session.movies.annotate(
            votes_count=Count('votes',
                              filter=Q(votes__vote_session=vote_session))
        )
        context["vote_count"] = movies_with_votes

        return context

class VoteSessionCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = VoteSessionCreateForm
    template_name = "movies/vote_session/vote_session_form.html"
    success_url = reverse_lazy("movies:vote-session-list")

    def form_valid(self, form):
        response = super().form_valid(form)  # зберігає обʼєкт
        self.object.members.add(self.request.user)
        return response


@login_required
def vote_session_leave(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden()
    vote_session = get_object_or_404(VoteSession, pk=pk)
    vote_session.members.remove(request.user)
    if vote:= Vote.objects.filter(
        vote_session=vote_session,
        user=request.user):
        vote.delete()
    vote_sessions = VoteSession.objects.all()
    active_events = VoteSession.objects.filter(
        event_date_time__gt=timezone.now())
    return render(
        request,
        "movies/vote_session/partial/vote_session_partial.html",
        {
            "vote_sessions": vote_sessions,
            "active_events": active_events,
            "user": request.user,
        }
    )


@login_required
def movie_vote(request, pk_v, pk_m):
    if request.method != "POST":
        return HttpResponseForbidden()
    vote_session = get_object_or_404(VoteSession, pk=pk_v)
    movie = get_object_or_404(Movie, pk=pk_m)
    Vote.objects.create(user=request.user, movie=movie,
                        vote_session=vote_session)
    return redirect("movies:vote-session-detail", pk=vote_session.pk)


