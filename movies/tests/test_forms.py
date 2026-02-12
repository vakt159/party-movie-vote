from datetime import timedelta

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from movies.forms.add_movie_to_vote_session_form import \
    AddMovieToVoteSessionForm
from movies.forms.comment_forms import CommentForm
from movies.forms.vote_session_create_form import VoteSessionCreateForm
from movies.models import VoteSession, Movie, Comment

User = get_user_model()


class AddMovieToVoteSessionFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="pass1234"
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            password="pass1234"
        )

        self.movie = Movie.objects.create(
            name="Matrix",
            release_year=1999,
            description="Sci-fi",
            imdb_url="https://imdb.com"
        )

        self.other_movie = Movie.objects.create(
            name="Avatar",
            release_year=2009,
            description="Sci-fi",
            imdb_url="https://imdb.com"
        )
        self.session_available = VoteSession.objects.create(
            name="Session 1",
            event_date_time="2030-01-01 12:00"
        )
        self.session_available.members.add(self.user)
        self.session_available.movies.add(self.other_movie)

        self.session_with_movie = VoteSession.objects.create(
            name="Session 2",
            event_date_time="2030-01-02 12:00"
        )
        self.session_with_movie.members.add(self.user)
        self.session_with_movie.movies.add(self.movie)

        self.session_other_user = VoteSession.objects.create(
            name="Session 3",
            event_date_time="2030-01-03 12:00"
        )
        self.session_other_user.members.add(self.other_user)

    def test_queryset_with_user_and_movie(self):
        form = AddMovieToVoteSessionForm(
            user=self.user,
            movie=self.movie
        )

        qs = form.fields["vote_sessions"].queryset

        self.assertIn(self.session_available, qs)
        self.assertNotIn(self.session_with_movie, qs)
        self.assertNotIn(self.session_other_user, qs)

    def test_queryset_without_user(self):
        form = AddMovieToVoteSessionForm(movie=self.movie)

        qs = form.fields["vote_sessions"].queryset
        self.assertEqual(qs.count(), 0)

    def test_queryset_without_movie(self):
        form = AddMovieToVoteSessionForm(user=self.user)

        qs = form.fields["vote_sessions"].queryset
        self.assertEqual(qs.count(), 0)

    def test_form_valid_with_empty_selection(self):
        form = AddMovieToVoteSessionForm(
            data={},
            user=self.user,
            movie=self.movie
        )

        self.assertTrue(form.is_valid())

class CommentFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="pass1234"
        )

        self.movie = Movie.objects.create(
            name="Matrix",
            release_year=1999,
            description="Sci-fi",
            imdb_url="https://imdb.com"
        )

    def test_form_valid_with_text(self):
        form = CommentForm(data={
            "text": "Great movie!"
        })

        self.assertTrue(form.is_valid())

    def test_form_invalid_without_text(self):
        form = CommentForm(data={})

        self.assertFalse(form.is_valid())
        self.assertIn("text", form.errors)

    def test_form_saves_comment(self):
        form = CommentForm(data={
            "text": "Amazing!"
        })

        self.assertTrue(form.is_valid())

        comment = form.save(commit=False)
        comment.user = self.user
        comment.movie = self.movie
        comment.save()

        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(comment.text, "Amazing!")
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.movie, self.movie)

    def test_text_widget_is_textarea(self):
        form = CommentForm()

        field = form.fields["text"]
        widget = field.widget

        self.assertEqual(widget.__class__.__name__, "Textarea")
        self.assertEqual(widget.attrs["rows"], 4)
        self.assertEqual(widget.attrs["cols"], 50)
        self.assertEqual(
            widget.attrs["placeholder"],
            "Enter your comment here..."
        )


class VoteSessionCreateFormTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1",
            password="pass1234"
        )
        self.user2 = User.objects.create_user(
            username="user2",
            password="pass1234"
        )

        self.movie1 = Movie.objects.create(
            name="Matrix",
            release_year=1999,
            description="Sci-fi",
            imdb_url="https://imdb.com"
        )
        self.movie2 = Movie.objects.create(
            name="Avatar",
            release_year=2009,
            description="Sci-fi",
            imdb_url="https://imdb.com"
        )

        self.future_datetime = (
            timezone.now() + timedelta(days=1)
        ).strftime('%Y-%m-%dT%H:%M')

    def test_form_valid_with_movies(self):
        form = VoteSessionCreateForm(data={
            "name": "Evening Movie",
            "members": [self.user1.id, self.user2.id],
            "movies": [self.movie1.id, self.movie2.id],
            "event_date_time": self.future_datetime
        })

        self.assertTrue(form.is_valid())

    def test_form_invalid_without_movies(self):
        form = VoteSessionCreateForm(data={
            "name": "Evening Movie",
            "members": [self.user1.id],
            "movies": [],
            "event_date_time": self.future_datetime
        })

        self.assertFalse(form.is_valid())
        self.assertIn("movies", form.errors)
        self.assertEqual(
            form.errors["movies"][0],
            "This field is required."
        )

    def test_form_saves_vote_session(self):
        form = VoteSessionCreateForm(data={
            "name": "Friday Night",
            "members": [self.user1.id],
            "movies": [self.movie1.id],
            "event_date_time": self.future_datetime
        })

        self.assertTrue(form.is_valid())

        vote_session = form.save()

        self.assertEqual(VoteSession.objects.count(), 1)
        self.assertEqual(vote_session.name, "Friday Night")
        self.assertIn(self.user1, vote_session.members.all())
        self.assertIn(self.movie1, vote_session.movies.all())

    def test_members_field_is_optional(self):
        form = VoteSessionCreateForm(data={
            "name": "Solo Event",
            "movies": [self.movie1.id],
            "event_date_time": self.future_datetime
        })

        self.assertTrue(form.is_valid())

    def test_event_date_time_widget_attrs(self):
        form = VoteSessionCreateForm()
        widget = form.fields["event_date_time"].widget

        self.assertEqual(widget.input_type, "datetime-local")
        self.assertIn("min", widget.attrs)
        self.assertEqual(widget.attrs["class"], "form-control")
