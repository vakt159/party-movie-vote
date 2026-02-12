from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views import generic

from movies.forms.comment_forms import CommentForm
from movies.models import Movie, Comment


class MovieDetailView(LoginRequiredMixin, generic.DetailView):
    model = Movie
    template_name = "movies/movie/movie_detail.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = Comment.objects.filter(movie_id=context["movie"].id)
        form = CommentForm()
        context["comments"] = comments
        context["form"] = form
        return context


class MovieCreateView(generic.CreateView):
    model = Movie
    fields = "__all__"
    template_name = "movies/movie/movie_form.html"
    success_url = reverse_lazy("movies:movies-list")


class MovieUpdateView(generic.UpdateView):
    model = Movie
    fields = "__all__"
    template_name = "movies/movie/movie_form.html"
    success_url = reverse_lazy("movies:movies-list")

class MovieListView(LoginRequiredMixin, generic.ListView):
    model = Movie
    template_name = "movies/movie/movie_list.html"


class MovieListPartialView(LoginRequiredMixin, generic.ListView):
    model = Movie
    template_name = "movies/movie/partial/movie_list_partial.html"

    def get_queryset(self):
        queryset = Movie.objects.all()
        if search := self.request.GET.get("search"):
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(director__icontains=search)
                | Q(description__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        return context
