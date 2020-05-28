'''
File - home/views.py
Creator - chrislockard21

Used to render the pages associated with the home application. These views
also leverage the models created in the other applications to give the user
more information on login. This file also contains a Statistics object to
make the collection of statistics OOP.
'''


# Imports ----------------------------------------------------------------------

from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from .forms import RegisterForm
from django.contrib.auth import login, authenticate
from django.views import generic, View
from workout.models import Workout, Exercise, ExerciseByGroup
from log.models import Log, Set, SetHistory, LogHistory
from django.db.models import Count
from workout.forms import WorkoutCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from home.statistics import Statistics

# ------------------------------------------------------------------------------


# Views ------------------------------------------------------------------------

class Index(View):
    '''Renders the index page for the user'''
    template_name = 'home/index.html'
    form_class = WorkoutCreationForm

    def get(self, request):
        if request.user.is_authenticated:
            form = self.form_class(None)
            statistics = Statistics(request)
            context = {
                'workouts': statistics.workouts_and_exercises(),
                'log_set': statistics.log_widget(),
                'log_count': statistics.log_count(),
                'open_log_count': statistics.open_log_count(),
                'max_exercise': statistics.max_exercise(),
                'volume': statistics.total_volume(),
                'logged_in': True,
                'form': form,
            }

        else:
            context = {
                'workout_message': 'You need to login to save workouts.',
                'logging_message': 'You need to login to save logs.',
                'statistics_message': 'You need to login to see statistics.'
            }

        return render(request, self.template_name, context)

class Register(generic.edit.FormView):
    template_name = 'home/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('home:index')

    def form_valid(self, form):
        '''Handles the form when valid'''
        user = form.save(commit=False)

        # Gets the cleaned form data
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']

        # Gets and sets the users password
        if password == form.cleaned_data['password2']:
            user.set_password(password)
            user.save()

            # Authenticates the user for initial login
            user = authenticate(username=username, password=password)
            if user is not None:
                # Logs in the user
                if user.is_active:
                    login(self.request, user)

        return super(Register, self).form_valid(form)

class AboutView(generic.TemplateView):
    template_name = "home/about.html"

# ------------------------------------------------------------------------------
