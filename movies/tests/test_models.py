from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from movies.models import (
    Movie,
    Comment,
    MovieSession,
    VoteSession,
    Vote,
)


User = get_user_model()


class MovieModelTests(TestCase):

    def test_movie_creation(self):
        movie = Movie.objects.create(
            name="Matrix",
            release_year=1999,
            director="Wachowski",
            description="Sci-fi",
            imdb_url="https://imdb.com"
        )

        self.assertEqual(movie.name, "Matrix")
        self.assertEqual(movie.release_year, 1999)
        self.assertEqual(movie.director, "Wachowski")

    def test_release_year_validation(self):
        movie = Movie(
            name="Old Movie",
            release_year=1800,
            description="Test",
            imdb_url="https://imdb.com"
        )

        with self.assertRaises(ValidationError):
            movie.full_clean()


class CommentModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("user", "pass1234")
        self.movie = Movie.objects.create(
            name="Matrix",
            description="Sci-fi",
            imdb_url="https://imdb.com"
        )

    def test_comment_creation(self):
        comment = Comment.objects.create(
            user=self.user,
            movie=self.movie,
            text="Great movie"
        )

        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.movie, self.movie)
        self.assertEqual(comment.text, "Great movie")

    def test_comment_deleted_with_movie(self):
        Comment.objects.create(
            user=self.user,
            movie=self.movie,
            text="Test"
        )

        self.movie.delete()
        self.assertEqual(Comment.objects.count(), 0)


class MovieSessionModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("user", "pass1234")
        self.movie = Movie.objects.create(
            name="Matrix",
            description="Sci-fi",
            imdb_url="https://imdb.com"
        )

    def test_movie_session_creation(self):
        session = MovieSession.objects.create(
            name="Evening",
            movie=self.movie,
            event_date_time=timezone.now()
        )
        session.members.add(self.user)

        self.assertIn(self.user, session.members.all())
        self.assertEqual(session.movie, self.movie)

    def test_movie_set_null_on_delete(self):
        session = MovieSession.objects.create(
            name="Session",
            movie=self.movie,
            event_date_time=timezone.now()
        )

        self.movie.delete()
        session.refresh_from_db()

        self.assertIsNone(session.movie)


class VoteSessionModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("user", "pass1234")
        self.movie = Movie.objects.create(
            name="Matrix",
            description="Sci-fi",
            imdb_url="https://imdb.com"
        )

    def test_vote_session_creation(self):
        vote_session = VoteSession.objects.create(
            name="Voting",
            event_date_time=timezone.now()
        )
        vote_session.members.add(self.user)
        vote_session.movies.add(self.movie)

        self.assertIn(self.user, vote_session.members.all())
        self.assertIn(self.movie, vote_session.movies.all())


class VoteModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("user", "pass1234")
        self.movie = Movie.objects.create(
            name="Matrix",
            description="Sci-fi",
            imdb_url="https://imdb.com"
        )
        self.vote_session = VoteSession.objects.create(
            name="Voting",
            event_date_time=timezone.now()
        )

    def test_vote_creation(self):
        vote = Vote.objects.create(
            user=self.user,
            movie=self.movie,
            vote_session=self.vote_session
        )

        self.assertEqual(vote.user, self.user)
        self.assertEqual(vote.movie, self.movie)
        self.assertEqual(vote.vote_session, self.vote_session)

    def test_votes_deleted_with_vote_session(self):
        Vote.objects.create(
            user=self.user,
            movie=self.movie,
            vote_session=self.vote_session
        )

        self.vote_session.delete()
        self.assertEqual(Vote.objects.count(), 0)
