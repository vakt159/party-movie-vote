from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from movies.models import Movie, Comment, MovieSession, VoteSession, Vote

User = get_user_model()


class BaseCommentViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="pass1234"
        )

        self.movie = Movie.objects.create(
            name="Matrix",
            description="Sci-fi",
            imdb_url="https://imdb.com"
        )

        self.comment = Comment.objects.create(
            user=self.user,
            movie=self.movie,
            text="Initial comment"
        )


class CommentCreateViewTests(BaseCommentViewTest):

    def test_login_required(self):
        url = reverse("movies:comment-create", kwargs={"pk": self.movie.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_create_comment(self):
        self.client.login(username="testuser", password="pass1234")

        url = reverse("movies:comment-create", kwargs={"pk": self.movie.id})
        response = self.client.post(url, {
            "text": "New comment"
        })

        self.assertEqual(Comment.objects.count(), 2)

        comment = Comment.objects.latest("id")
        self.assertEqual(comment.text, "New comment")
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.movie, self.movie)

        self.assertRedirects(
            response,
            reverse("movies:movie-detail", kwargs={"pk": self.movie.id})
        )


class CommentUpdateViewTests(BaseCommentViewTest):

    def test_update_comment(self):
        self.client.login(username="testuser", password="pass1234")

        url = reverse("movies:comment-update", kwargs={"pk": self.comment.id})
        response = self.client.post(url, {
            "text": "Updated text"
        })

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, "Updated text")

        self.assertRedirects(
            response,
            reverse("movies:movie-detail", kwargs={"pk": self.movie.id})
        )


class CommentDeleteViewTests(BaseCommentViewTest):

    def test_delete_comment(self):
        self.client.login(username="testuser", password="pass1234")

        url = reverse("movies:comment-delete", kwargs={"pk": self.comment.id})
        response = self.client.post(url)

        self.assertEqual(Comment.objects.count(), 0)

        self.assertRedirects(
            response,
            reverse("movies:movie-detail", kwargs={"pk": self.movie.id})
        )


class MovieSessionDetailViewTests(TestCase):

    def setUp(self):
        self.movie = Movie.objects.create(
            name="Matrix",
            description="Sci-fi",
            imdb_url="https://imdb.com"
        )

        self.movie_session = MovieSession.objects.create(
            name="Evening Session",
            movie=self.movie,
            event_date_time=timezone.now()
        )

    def test_movie_session_detail_view(self):
        url = reverse(
            "movies:movie-session-detail",
            kwargs={"pk": self.movie_session.id}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.context["movie_session"],
            self.movie_session
        )

        self.assertIn("winner", response.context)
        self.assertEqual(
            response.context["winner"],
            self.movie
        )

        self.assertTemplateUsed(
            response,
            "movies/movie_session/movie_session_detail.html"
        )


class MovieViewTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="test12345"
        )

        self.movie = Movie.objects.create(
            name="Inception",
            director="Nolan",
            description="Dreams",
            imdb_url="https://imdb.com"
        )

    def test_movie_detail_login_required(self):
        url = reverse("movies:movie-detail", kwargs={"pk": self.movie.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_movie_detail_view(self):
        self.client.login(username="testuser", password="test12345")

        Comment.objects.create(
            user=self.user,
            movie=self.movie,
            text="Great movie"
        )

        url = reverse("movies:movie-detail", kwargs={"pk": self.movie.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["movie"], self.movie)
        self.assertEqual(len(response.context["comments"]), 1)
        self.assertIn("form", response.context)
        self.assertTemplateUsed(response, "movies/movie/movie_detail.html")

    def test_movie_create_view(self):
        url = reverse("movies:movie-create")
        self.client.force_login(self.user)
        response = self.client.post(url, {
            "name": "Matrix",
            "director": "Wachowski",
            "description": "Sci-fi",
            "imdb_url": "https://imdb.com"
        })

        self.assertEqual(Movie.objects.count(), 2)
        self.assertRedirects(response, reverse("movies:movies-list"))

    def test_movie_update_view(self):
        url = reverse("movies:movie-update", kwargs={"pk": self.movie.id})

        response = self.client.post(url, {
            "name": "Inception Updated",
            "director": "Nolan",
            "description": "Updated",
            "imdb_url": "https://imdb.com"
        })

        self.movie.refresh_from_db()
        self.assertEqual(self.movie.name, "Inception Updated")

    def test_movie_list_view_login_required(self):
        url = reverse("movies:movies-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_movie_list_view(self):
        self.client.login(username="testuser", password="test12345")

        url = reverse("movies:movies-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inception")
        self.assertTemplateUsed(response, "movies/movie/movie_list.html")

    def test_movie_list_partial_view(self):
        self.client.login(username="testuser", password="test12345")

        url = reverse("movies:movie-list-partial")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inception")

    def test_movie_list_partial_search(self):
        self.client.login(username="testuser", password="test12345")

        url = reverse("movies:movie-list-partial")
        response = self.client.get(url, {"search": "Nolan"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inception")


class UserViewsTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="test12345"
        )

    def test_user_detail_login_required(self):
        url = reverse("movies:user-detail", kwargs={"pk": self.user.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_user_detail_view_active_events(self):
        self.client.login(username="testuser", password="test12345")

        active_session = VoteSession.objects.create(
            name="Active",
            event_date_time=timezone.now() + timedelta(hours=1)
        )

        past_session = VoteSession.objects.create(
            name="Past",
            event_date_time=timezone.now() - timedelta(hours=1)
        )

        url = reverse("movies:user-detail", kwargs={"pk": self.user.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn(active_session, response.context["active_events"])
        self.assertNotIn(past_session, response.context["active_events"])
        self.assertTemplateUsed(response, "movies/user/user_detail.html")

    def test_index_redirect_authenticated(self):
        self.client.login(username="testuser", password="test12345")

        response = self.client.get(reverse("movies:index"))

        self.assertRedirects(
            response,
            reverse("movies:user-detail", kwargs={"pk": self.user.pk})
        )


class VoteSessionViewsTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="user",
            password="test12345"
        )

        self.movie1 = Movie.objects.create(
            name="Movie 1",
            description="Desc",
            imdb_url="https://imdb.com/1"
        )

        self.movie2 = Movie.objects.create(
            name="Movie 2",
            description="Desc",
            imdb_url="https://imdb.com/2"
        )

        self.vote_session = VoteSession.objects.create(
            name="Session",
            event_date_time=timezone.now() + timedelta(hours=1)
        )
        self.vote_session.movies.set([self.movie1, self.movie2])
        self.vote_session.members.add(self.user)

    def test_vote_session_list_login_required(self):
        response = self.client.get(
            reverse("movies:vote-session-list")
        )
        self.assertEqual(response.status_code, 302)


    def test_add_movie_to_vote_session(self):
        self.client.login(username="user", password="test12345")

        url = reverse(
            "movies:add-movie-to-vote-session",
            kwargs={"pk": self.movie1.pk}
        )

        response = self.client.post(url, {
            "vote_sessions": [self.vote_session.pk]
        })

        self.vote_session.refresh_from_db()
        self.assertIn(self.movie1, self.vote_session.movies.all())

    def test_vote_session_join(self):
        self.client.login(username="user", password="test12345")

        new_user = get_user_model().objects.create_user(
            username="user2",
            password="pass123"
        )
        self.client.login(username="user2", password="pass123")

        response = self.client.post(
            reverse("movies:vote-session-join",
                    kwargs={"pk": self.vote_session.pk})
        )

        self.vote_session.refresh_from_db()
        self.assertIn(new_user,
                      self.vote_session.members.all())
        self.assertEqual(response.status_code, 200)

    def test_movie_vote_creates_vote(self):
        self.client.login(username="user", password="test12345")

        url = reverse(
            "movies:movie-vote",
            kwargs={
                "pk_v": self.vote_session.pk,
                "pk_m": self.movie1.pk
            }
        )

        response = self.client.post(url)

        self.assertEqual(
            Vote.objects.filter(
                user=self.user,
                vote_session=self.vote_session,
                movie=self.movie1
            ).count(),
            1
        )

        self.assertRedirects(
            response,
            reverse(
                "movies:vote-session-detail",
                kwargs={"pk": self.vote_session.pk}
            )
        )

    def test_vote_session_detail_winner_by_votes(self):
        Vote.objects.create(
            user=self.user,
            movie=self.movie1,
            vote_session=self.vote_session
        )

        self.client.login(username="user", password="test12345")

        response = self.client.get(
            reverse(
                "movies:vote-session-detail",
                kwargs={"pk": self.vote_session.pk}
            )
        )

        self.assertEqual(
            response.context["vote_count"]
            .get(id=self.movie1.id)
            .votes_count,
            1
        )

    def test_vote_session_detail_random_winner_if_no_votes(self):
        self.client.login(username="user", password="test12345")

        response = self.client.get(
            reverse(
                "movies:vote-session-detail",
                kwargs={"pk": self.vote_session.pk}
            )
        )

        result = response.context.get("result")
        self.assertIsNotNone(result)
        self.assertIn(
            result.movie,
            self.vote_session.movies.all()
        )

    def test_vote_session_create_adds_creator(self):
        self.client.login(username="user", password="test12345")

        response = self.client.post(
            reverse("movies:vote-session-create"),
            {
                "name": "New session",
                "movies": [self.movie1.pk],
                "event_date_time": (
                        timezone.now() + timedelta(hours=3)
                ).strftime("%Y-%m-%dT%H:%M")
            }
        )

        session = VoteSession.objects.get(name="New session")
        self.assertIn(self.user, session.members.all())
