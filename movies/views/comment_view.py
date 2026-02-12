from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.views import generic, View

from movies.forms.comment_forms import CommentForm
from movies.models import Comment, Movie


class CommentCreateView(LoginRequiredMixin, generic.CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "movies/movie/movie_detail.html"
    context_object_name = "comment"

    def form_valid(self, form):
        form.instance.user = self.request.user
        movie = get_object_or_404(Movie, pk=self.kwargs["pk"])
        form.instance.movie = movie
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie = get_object_or_404(Movie, pk=self.kwargs["pk"])
        context["movie"] = movie
        context["comments"] = Comment.objects.filter(movie=movie)
        return context

    def get_success_url(self):
        return reverse(
            "movies:movie-detail",
            kwargs={"pk": self.object.movie.id}
        )

class CommentUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "movies/movie/movie_detail.html"
    context_object_name = "comment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie = self.object.movie
        context["movie"] = movie
        context["comments"] = Comment.objects.filter(movie=movie)
        return context

    def get_success_url(self):
        return reverse("movies:movie-detail", kwargs={"pk": self.object.movie.id})

class CommentDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Comment
    template_name = "movies/movie/comment_confirm_delete.html"
    def get_success_url(self):
        return reverse("movies:movie-detail", kwargs={"pk": self.object.movie.id})
