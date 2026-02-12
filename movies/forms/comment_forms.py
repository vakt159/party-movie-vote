from django import forms

from movies.models import Comment


class CommentForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 4,
                'cols': 50,
                'placeholder': 'Enter your comment here...',
            }
        )
    )

    class Meta:
        model = Comment
        fields = ("text",)
