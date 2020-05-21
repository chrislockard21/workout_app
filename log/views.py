from .models import Log, Set, SetHistory, LogHistory
from workout.models import Workout
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import modelformset_factory
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseServerError, Http404, HttpResponse
from django import forms
from workout.models import Workout, Exercise
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from .forms import SetForm
from datetime import datetime, date, timedelta
from user_profile.models import OneRepMax

def log_volume(log):
    '''Function to caluclate volume of a log'''
    volume = 0
    log_sets = Set.objects.filter(log=log)
    for set in log_sets:
        if set.unit == 'lbs':
            volume += set.weight*set.reps
        else:
            volume += set.weight*2.20462*set.reps
    return volume

# Create your views here.

class LogCreate(LoginRequiredMixin, View):
    '''
    Responsible for creating a new workout which will collect the sets created
    by the user for better reporting. Workout to sets will be one to many. The
    user will never see this view rendered, it is responsible only for creating
    the object
    '''
    login_url = 'home:login'

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

class LogDetail(LoginRequiredMixin, View):
    '''
    This view renders an individual log so that users can select exercises to
    edit
    '''
    login_url = 'home:login'
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

class LogExerciseSetAdd(LoginRequiredMixin, View):
    '''
    Allows users to add sets to an exercise one by one to not create too many
    forms on one page. After adding a set they are directed to the same page
    with either the new set or form errors
    '''
    login_url = 'home:login'
    template_name = 'log/log_exercise_set_add.html'
    # SetCreationFormset = inlineformset_factory(Exercise, Set, form=LiftingSetForm, can_delete=True, extra=0)

    def get(self, request, log_pk, exercise_pk):
        '''
        Creates the GET method for the set add view
        '''
        # Gets required objects
        log = get_object_or_404(Log, pk=log_pk)
        exercise = get_object_or_404(Exercise, pk=exercise_pk)
        if exercise.user == self.request.user:
            form = SetForm(None)
            sets = Set.objects.filter(exercise=exercise, log=log)
            history = SetHistory.objects.filter(exercise=exercise.exercise).order_by('-created_at')[:5]
            try:
                pr = OneRepMax.objects.get(user=request.user, exercise=exercise.exercise)
            except:
                pr = None
            context = {
                'form': form,
                'sets': sets,
                'log': log,
                'pr': pr,
                'exercise': exercise,
                'history': history,
            }
            return render(request, self.template_name, context)
        else:
            Http404('This is not your exercise.')

    def post(self, request, log_pk, exercise_pk):
        '''
        Creates the POST method for the set add view and processes the form data
        sent
        '''
        # Gets required objects
        log = get_object_or_404(Log, pk=log_pk)
        exercise = get_object_or_404(Exercise, pk=exercise_pk)
        if exercise.user == self.request.user:
            sets = Set.objects.filter(exercise=exercise)
            form = SetForm(self.request.POST)

            # Checks for a valid form (number values in the forms etc.)
            if form.is_valid():
                set = form.save(commit=False)
                set.user = self.request.user
                set.log = log
                set.exercise = exercise
                set.save()

                # Gathers keys for the reverse function so that the url can be
                # found
                kwargs = {
                    'log_pk': log_pk,
                    'exercise_pk': exercise_pk,
                }
                return HttpResponseRedirect(reverse('log:log_exercise_set_add', kwargs=kwargs))

            # Pass form errors to view context if the form is not valid
            else:
                try:
                    pr = OneRepMax.objects.filter(user=request.user, exercise=exercise.exercise)
                except:
                    pr = None
                history = SetHistory.objects.filter(exercise=exercise.exercise).order_by('-created_at')[:5]
                context = {
                    'form': form,
                    'sets': sets,
                    'log': log,
                    'pr': pr,
                    'exercise': exercise,
                    'history': history,
                }
                return render(request, self.template_name, context)
        else:
            Http404('This is not your exercise')

def create_history(sets, request, log_history):
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

class LogClose(LoginRequiredMixin, View):
    '''
    View to set the log to close and log sets into history.
    '''
    login_url = 'home:login'

    def get(self, request, log_pk):
        log = get_object_or_404(Log, pk=log_pk)
        if log.user == self.request.user:
            if log.status == 'open':
                # creates a history object for each set so that deleting
                # exercises will not delete the users history
                # Gets all sets
                sets = Set.objects.filter(log=log)
                log_history = LogHistory.objects.create(user=request.user, workout=log.workout)

                create_history(sets, request, log_history)

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
    login_url = "home:login"

    def get_object(self):
        '''
        Defines what object to get on delete
        '''
        id_ = self.kwargs.get("set_pk")
        return get_object_or_404(Set, id=id_)

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
                return Http404('This is not your set.')
