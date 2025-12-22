from django import forms

from movies.models import VoteSession


class AddMovieToVoteSessionForm(forms.Form):
    vote_sessions = forms.ModelMultipleChoiceField(
        queryset=VoteSession.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Available events",
    )

    def __init__(self, *args, user=None, movie=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user and movie:
            self.fields["vote_sessions"].queryset = (
                VoteSession.objects
                .filter(members=user)
                .exclude(movies=movie)
            )