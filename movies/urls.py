from django.urls import path
from movies import views
from movies.views import vote_session_view
from movies.views.comment_view import (CommentCreateView,
                                       CommentUpdateView,
                                       CommentDeleteView)
from movies.views.movie_session_view import MovieSessionDetailView
from movies.views.movie_view import (MovieListView,
                                     MovieDetailView,
                                     MovieCreateView,
                                     MovieUpdateView,
                                     MovieListPartialView)
from movies.views.user_view import UserDetailView, SignUpView
from movies.views.vote_session_view import (VoteSessionListView,
                                            VoteSessionListPartialView,
                                            VoteSessionDetailView,
                                            AddMovieToVoteSessionView,
                                            VoteSessionCreateView,
                                            )

app_name = "movies"

urlpatterns = [
    path("movies",
         MovieListView.as_view(),
         name="movies-list"),
    path("movies/partial/",
         MovieListPartialView.as_view(),
         name="movie-list-partial"),
    path("movies/<int:pk>/",
         MovieDetailView.as_view(),
         name="movie-detail"),
    path("movies/create/",
         MovieCreateView.as_view(),
         name="movie-create"),
    path("movies/<int:pk>/update/",
         MovieUpdateView.as_view(),
         name="movie-update"),
    path(
        "movies/<int:pk>/comments/create/",
        CommentCreateView.as_view(),
        name="comment-create"
    ),
    path("comments/<int:pk>/update/", CommentUpdateView.as_view(),
         name="comment-update"),
    path("comments/<int:pk>/delete/", CommentDeleteView.as_view(),
         name="comment-delete"),
    path("votesessions/", VoteSessionListView.as_view(),
         name="vote-session-list"),
    path("votesessions/partial/",
         VoteSessionListPartialView.as_view(),
         name="vote-session-list-partial"),
    path("votesessions/<int:pk>/",
         VoteSessionDetailView.as_view(),
         name="vote-session-detail"),
    path("profile/",
         UserDetailView.as_view(),
         name="user-detail"),
    path("", views.user_view.index, name="index"),

    path(
        "movies/<int:pk>/add-to-vote-session/",
        AddMovieToVoteSessionView.as_view(),
        name="add-movie-to-vote-session"),
    path(
        "vote-sessions/<int:pk>/join/",
        vote_session_view.vote_session_join,
        name="vote-session-join"
    ),
    path(
        "vote-sessions/<int:pk>/leave/",
        vote_session_view.vote_session_leave,
        name="vote-session-delete-user"
    ),
    path(
        "vote-sessions/<int:pk_v>/movie/<int:pk_m>/vote",
        vote_session_view.movie_vote,
        name="movie-vote"
    ),
    path(
        "moviesession/<int:pk>/",
        MovieSessionDetailView.as_view(),
        name="movie-session-detail"
    ),
    path("vote-session/create/", VoteSessionCreateView.as_view(), name="vote-session-create"),
    path("signup/", SignUpView.as_view(), name="signup"),

]
