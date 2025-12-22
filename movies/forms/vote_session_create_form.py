from django.contrib.auth import get_user_model

from movies.models import VoteSession, Movie
from django import forms
from django.utils import timezone


class VoteSessionCreateForm(forms.ModelForm):
    name = forms.CharField()
    min_datetime = timezone.now().strftime('%Y-%m-%dT%H:%M')

    members = forms.ModelMultipleChoiceField(
        required=False,
        queryset=get_user_model().objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
    movies = forms.ModelMultipleChoiceField(
        queryset=Movie.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    event_date_time = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'min': min_datetime,
                'class': 'form-control'
            },
            format='%Y-%m-%dT%H:%M'
        )
    )

    class Meta:
        model = VoteSession
        fields = ("name", "members", "movies", "event_date_time")

    def clean_movies(self):
        movies = self.cleaned_data.get('movies')
        if not movies or movies.count() == 0:
            raise forms.ValidationError("Please select at least one movie.")
        return movies
