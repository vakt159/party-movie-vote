from django.contrib import admin
from .models import User, Movie, MovieSession, Comment, Vote, VoteSession


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "first_name", "last_name", "email", "is_staff")
    search_fields = ("username", "first_name", "last_name", "email")
    list_filter = ("is_staff", "is_superuser", "is_active")


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ("user", "text")
    can_delete = False


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("name", "director", "release_year", "imdb_url")
    search_fields = ("name", "director")
    list_filter = ("release_year",)
    inlines = [CommentInline]


@admin.register(MovieSession)
class MovieSessionAdmin(admin.ModelAdmin):
    list_display = ("name", "movie", "event_date_time")
    list_filter = ("event_date_time",)
    search_fields = ("name", "movie__name")
    filter_horizontal = ("members",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "movie", "short_text")
    search_fields = ("user__username", "movie__name", "text")
    list_filter = ("movie",)

    def short_text(self, obj):
        return (obj.text[:50] + "...") if len(obj.text) > 50 else obj.text
    short_text.short_description = "Comment"


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("user", "movie", "vote_session")
    list_filter = ("vote_session", "movie")
    search_fields = ("user__username", "movie__name", "vote_session__name")


@admin.register(VoteSession)
class VoteSessionAdmin(admin.ModelAdmin):
    list_display = ("name", "event_date_time", "movie_session")
    search_fields = ("name", "movie_session__name")
    list_filter = ("event_date_time",)
    filter_horizontal = ("members", "movies")

