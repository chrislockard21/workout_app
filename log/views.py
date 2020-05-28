from .models import Log, Set, SetHistory, LogHistory
from workout.models import Workout
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import modelformset_factory
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponseServerError, Http404, HttpResponse
from django import forms
from workout.models import Workout, Exercise, ExerciseByGroup
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from .forms import SetForm, ValidateExerciseForm
from datetime import datetime, date, timedelta
from user_profile.models import OneRepMax
from home.statistics import Statistics

# Create your views here.

class LogCreate(LoginRequiredMixin, View):
    '''
    Responsible for creating a new workout which will collect the sets created
    by the user for better reporting. Workout to sets will be one to many. The
    user will never see this view rendered, it is responsible only for creating
    the object
    '''
    login_url = 'login'

    def get(self, request, pk):
        '''
        Creates the GET method for the log create view
        '''
        # Get the workout that the user is trying to log
        user_workout = get_object_or_404(Workout, user=self.request.user, pk=pk)
        if user_workout.user == request.user:
            # Try to get the open log object for this workout, and if it exists
            # take the user to the open log entry
            try:
                user_workout = Log.objects.get(user=self.request.user, workout=user_workout, status='open')
                kwargs = {
                    'log_pk': user_workout.id,
                }
                return HttpResponseRedirect(reverse('log:log_detail', kwargs=kwargs))

            # If the obejct does not exists, create a new one and take the user to
            # the detail page for that log
            except ObjectDoesNotExist:
                new_workout = Log.objects.create(user=self.request.user, workout=user_workout, status='open')
                new_workout.save()
                kwargs = {
                    'log_pk': new_workout.id,
                }
                return HttpResponseRedirect(reverse('log:log_detail', kwargs=kwargs))
        else:
            return Http404('This is not your workout.')

# Re-write as detail view

class LogDetail(LoginRequiredMixin, View):
    '''
    This view renders an individual log so that users can select exercises to
    edit
    '''
    login_url = 'login'
    template_name = 'log/log_details.html'

    def get(self, request, log_pk):
        '''
        Creates the GET method for the log detail view
        '''
        log = get_object_or_404(Log, pk=log_pk)
        if log.user == self.request.user:
            exercises = Exercise.objects.filter(workout=log.workout)
            exercise_list = []
            for exercise in exercises:
                sets = Set.objects.filter(log=log, exercise=exercise)
                set_count = sets.count()
                volume = 0
                for set in sets:
                    if set.unit == 'lbs':
                        volume += set.weight*set.reps
                    else:
                        volume += set.weight*2.20462*set.reps

                exercise_list.append((exercise, set_count, volume))

            context = {
                'log': log,
                'exercise_list': exercise_list,
            }
            return render(request, self.template_name, context)
        else:
            Http404('This is not your log.')

class LogExerciseSetAdd(LoginRequiredMixin, generic.edit.FormView):
    '''Form view to allow users to add sets to a log'''
    login_url = 'login'
    template_name = 'log/log_exercise_set_add.html'
    form_class = SetForm

    def get_success_url(self, **kwargs):
        '''gets the success url with log/exercise kwargs'''
        return reverse_lazy(
            'log:log_exercise_set_add',
            kwargs = {
                'log_pk': self.kwargs.get('log_pk'),
                'exercise_pk': self.kwargs.get('exercise_pk')
            }
        )

    def get_context_data(self, **kwargs):
        '''Gets extra context data for the view'''
        context = super(LogExerciseSetAdd, self).get_context_data(**kwargs)
        log = get_object_or_404(Log, id=self.kwargs.get('log_pk'))
        context['log'] = log
        exercise = get_object_or_404(Exercise, id=self.kwargs.get('exercise_pk'))
        context['exercise'] = exercise
        if log.user == self.request.user:
            context['sets'] = Set.objects.filter(exercise=exercise, log=log)
            context['history'] = SetHistory.objects.filter(exercise=exercise.exercise).order_by('-created_at')[:5]
            try:
                context['pr'] = OneRepMax.objects.get(user=request.user, exercise=exercise.exercise)
            except:
                context['pr'] = None
        else:
            raise Http404
        return context

    def form_valid(self, form):
        '''Function executes if a form is valid'''
        log = get_object_or_404(Log, id=self.kwargs.get('log_pk'))
        exercise = get_object_or_404(Exercise, id=self.kwargs.get('exercise_pk'))
        if log.user == self.request.user:
            set = form.save(commit=False)
            set.user = self.request.user
            set.log = log
            set.exercise = exercise
            set.save()
            return super(LogExerciseSetAdd, self).form_valid(form)
        else:
            raise Http404

class LogClose(LoginRequiredMixin, View):
    '''
    View to set the log to close and log sets into history.
    '''
    login_url = 'login'

    def create_history(self, sets, request, log_history):
        for set in sets:
            new_history = SetHistory.objects.create(
                user=request.user,
                log_history = log_history,
                exercise = set.exercise.exercise,
                reps = set.reps,
                weight = set.weight,
                unit = set.unit,
                difficulty = set.difficulty,
                notes = set.notes
            )

    def get(self, request, log_pk):
        log = get_object_or_404(Log, pk=log_pk)
        if log.user == self.request.user:
            if log.status == 'open':
                # creates a history object for each set so that deleting
                # exercises will not delete the users history
                # Gets all sets
                sets = Set.objects.filter(log=log)
                log_history = LogHistory.objects.create(user=request.user, workout=log.workout)

                self.create_history(sets, request, log_history)

                # set log status to closed moving it to logical archive
                log.closed_at = datetime.now()
                log.status = 'closed'
                log.save()

                return HttpResponseRedirect(reverse('home:index'))
            else:
                return HttpResponse('This log has already been closed.')
        else:
            return Http404('This is not your log.')

class SetDelete(LoginRequiredMixin, generic.edit.DeleteView):
    '''Deletes the selected workout'''
    template_name = 'log/set_delete.html'
    login_url = "login"

    def get_object(self, queryset=None):
        '''Ensures the user owns the object'''
        obj = Set.objects.get(id=self.kwargs.get('set_pk'))
        if obj.user != self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        log_pk = self.kwargs.get('log_pk')
        exercise_pk = self.kwargs.get('exercise_pk')
        kwargs = {
            'log_pk': log_pk,
            'exercise_pk': exercise_pk,
        }
        return reverse('log:log_exercise_set_add', kwargs=kwargs)

    def post(self, request, set_pk, log_pk, exercise_pk):
        if 'cancel' in request.POST:
            kwargs = {
                'log_pk': log_pk,
                'exercise_pk': exercise_pk,
            }
            return HttpResponseRedirect(reverse('log:log_exercise_set_add', kwargs=kwargs))

        else:
            set = get_object_or_404(Set, id=set_pk)
            if set.user == self.request.user:
                return super(SetDelete, self).post(request)
            else:
                raise Http404

class StatisticsView(LoginRequiredMixin, generic.TemplateView):
    template_name = "log/statistics.html"

    def get_log_volume(self, log, sets):
        '''Gets volume of a log (modified from other functions)'''
        log_volume = 0
        for set in sets:
            if set.unit == 'lbs':
                log_volume += set.weight*set.reps
            else:
                log_volume += set.weight*2.20462*set.reps
        return log_volume

    def get_chart_data(self, user, exercise):
        '''Method to get the date and volume sum for the selected exercise'''
        logs = LogHistory.objects.filter(user=user).reverse()
        obs = {}
        for log in logs:
            sets = SetHistory.objects.filter(log_history=log, exercise=exercise)
            if len(sets) > 0:
                obs[log.created_at] = self.get_log_volume(log, sets)
        return obs

    def get_exercise_volume(self, user, exercise):
        sets = SetHistory.objects.filter(user=user, exercise=exercise)
        volume = 0
        for set in sets:
            if set.unit == 'lbs':
                volume += set.weight*set.reps
            else:
                volume += set.weight*2.20462*set.reps
        return volume

    def get_context_data(self, **kwargs):
        '''Gets extra context'''
        context = super().get_context_data(**kwargs)
        summary_statistics = Statistics(self.request)
        if kwargs.get('exercise'):
            context['selected_exercise'] = get_object_or_404(ExerciseByGroup, id=kwargs.get('exercise'))
            context['exercise_volume'] = '{:,}'.format(self.get_exercise_volume(kwargs.get('user'), kwargs.get('exercise')))
            context['chart_data'] = self.get_chart_data(kwargs.get('user'), kwargs.get('exercise'))
            context['exercise_freq'] = summary_statistics.exercise_use_rate(kwargs.get('exercise'))
        context['exercises'] = ExerciseByGroup.objects.all().order_by('exercise_name')
        context['log_count'] = summary_statistics.log_count()
        context['open_log_count'] = summary_statistics.open_log_count()
        context['max_exercise'] = summary_statistics.max_exercise()
        context['volume'] = summary_statistics.total_volume()
        context['frequency'] = summary_statistics.max_exercise()
        return context

    def post(self, request):
        form = ValidateExerciseForm(request.POST)
        if form.is_valid():
            exercise_pk = int(form.cleaned_data['exercise'])
        # After form is submitted, function will render its own context with
        # the exercise id in kwargs
        return render(request, self.template_name, context=self.get_context_data(user=request.user, exercise=exercise_pk))
