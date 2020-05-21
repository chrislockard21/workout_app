'''
File - home/views.py
Creator - chrislockard21

Used to render the pages associated with the home application. These views
also leverage the models created in the other applications to give the user
more information on login. This file also contains a Statistics object to
make the collection of statistics OOO.
'''


# Imports ----------------------------------------------------------------------

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.base import TemplateView
from .forms import RegisterForm
from django.contrib.auth import login, authenticate, logout
from django.views import generic, View
from workout.models import Workout, Exercise, ExerciseByGroup
from log.models import Log, Set, SetHistory, LogHistory
from django.db.models import Count
from workout.forms import WorkoutCreationForm

# ------------------------------------------------------------------------------


# Utilities --------------------------------------------------------------------

class Statistics():

    def __init__(self, request):
        self.user = request.user
        self.workouts = Workout.objects.filter(user=self.user)
        self.logs = Log.objects.filter(workout__in=self.workouts, status='open')
        self.log_history = LogHistory.objects.filter(user=self.user)

    def log_widget(self):
        '''Gets the data for the log widgets'''
        return {
            log:(
                Set.objects.filter(log=log).count(),
                Exercise.objects.filter(workout=log.workout).count()
            ) for log in self.logs
        }

    def total_volume(self):
        '''Gets the users total volume (will convert kg to lbs)'''
        volume = 0
        for log in self.log_history:
            sets = SetHistory.objects.filter(log_history=log)
            for set in sets:
                if set.unit == 'lbs':
                    volume += set.weight*set.reps
                else:
                    # Convert kg to lbs
                    volume += set.weight*2.20462*set.reps
        return round(volume, 2)

    def max_exercise(self):
        '''Gets the most used exercise by the user'''
        exercise_counts = Exercise.objects.filter(user=self.user).values('exercise').annotate(freq=Count('exercise'))
        exercise_dict = {}
        for record in exercise_counts:
            id = record['exercise']
            exercise =  get_object_or_404(ExerciseByGroup, id=id)
            exercise_dict[exercise] = record['freq']
        try:
            max_exercise_name = max(exercise_dict, key=exercise_dict.get)
            return (max_exercise_name, exercise_dict[max_exercise_name])
        except:
            return ('No exercises created', 0)


    def workouts_and_exercises(self):
        '''Gets a dictionary of all user workouts and their exercises'''
        return {workout:Exercise.objects.filter(workout=workout) for workout in self.workouts}

    def log_count(self):
        '''Gets the total log history count'''
        return self.log_history.count

    def open_log_count(self):
        '''Gets the total open log count'''
        return self.logs.count

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
            return render(request, self.template_name, context)

        else:
            context = {
                'workout_message': 'You need to login to save workouts.',
                'logging_message': 'You need to login to save logs.',
                'statistics_message': 'You need to login to see statistics.'
            }

        return render(request, self.template_name, context)

class Register(View):
    '''Handles user registration and renders the registration page'''
    form_class = RegisterForm
    template_name = 'home/register.html'

    def get(self, request):
        '''
        Defines the GET method for the registration page
        '''
        form = self.form_class(None)
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        '''
        Defines the POST method for the registration page and handles initial
        login
        '''
        form = self.form_class(request.POST)

        if form.is_valid():
            # Holds off on writing to the database
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
                        login(request, user)
                        return redirect('home:index')

        return render(request, self.template_name, {'form':form})

class Logout(TemplateView):
    '''Logs the user out of the current session'''
    template_name = 'home/logout.html'

    def get(self, request):
        logout(request)
        return redirect('home:index')

class Login(View):
    '''Renders the login page'''
    template_name = 'home/login.html'

    def get(self, request):
        '''
        Defines the GET method for the login page
        '''
        return render(request, self.template_name)

    def post(self, request):
        '''
        Defines the POST method for the login page
        '''
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home:index')
        else:
            login_failed = True
            return render(request, self.template_name, {'login_failed':login_failed})

# ------------------------------------------------------------------------------
