from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic
from django.utils import timezone
from django.views.generic import CreateView

from movies.forms.sign_up_form import SignUpForm
from movies.models import VoteSession


class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = get_user_model()
    template_name = "movies/user/user_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_events"] = VoteSession.objects.filter(
            event_date_time__gt=timezone.now())
        return context


def index(request):
    if request.user.is_authenticated:
        return redirect(
            "movies:user-detail",
            pk=request.user.pk
        )
    return redirect("login")

class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("movies:movies-list")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response
