from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    """Define appearance and url for form based on User model"""
    form_class = CreationForm
    success_url = reverse_lazy('index')
    template_name = 'signup.html'
