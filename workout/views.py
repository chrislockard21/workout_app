'''
File - workout/views.py
Creator - chrislockard21

Used to render the pages for the workout application.
'''


# Imports ----------------------------------------------------------------------

from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic, View
from .models import Workout, Exercise, ExerciseByGroup
from .forms import WorkoutCreationForm, ExerciseForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django import forms
from log.models import Log, Set

# ------------------------------------------------------------------------------

class WorkoutInfo():
    '''Class to gather information on a workout'''
    def __init__(self, request, pk):
        self.user = request.user
        self.workout = Workout.objects.get(id=pk)
        self.logs =  Log.objects.filter(workout=self.workout, status='closed').order_by('-created_at')

    def get_workout_exercises(self):
        '''Get all exercises for the workout'''
        return Exercise.objects.filter(workout=self.workout)

    def get_log_count(self):
        '''Get the log count for workout'''
        return self.logs.count()

    def get_latest_log(self):
        '''Gets the latest log if there is one'''
        if len(self.logs) > 0:
            return self.logs[0]
        else:
            return None

    def get_graph_logs(self):
        '''Gets the logs ordered correctly for graphing'''
        logs_ordered = self.logs.reverse()
        if len(logs_ordered) >= 5:
            return logs_ordered[len(logs_ordered) - 5:]
        else:
            return logs_ordered

# Views ------------------------------------------------------------------------

class WorkoutCreate(LoginRequiredMixin, View):
    '''
    Renders the workout create page and allows users to create workouts and
    exercises on one page
    '''
    # Class attributes to store template information and login controls
    template_name = 'workout/workout_create.html'
    login_url = 'home:login'
    form_class = WorkoutCreationForm

    def post(self, request):
        '''
        Creates the POST method for the create view. This method will validate
        and create the new workout
        '''
        # Submits the posted data to the workout form and the exercise formset
        form = self.form_class(self.request.POST)
        # Checks if both forms are valid
        if form.is_valid():
            workout = form.save(commit=False)
            existing_workout_names = Workout.objects.filter(
                user=self.request.user
            ).values_list('workout_name', flat=True)

            # Checks if posted name already exists (considering capitalization)
            if form.cleaned_data['workout_name'] in existing_workout_names:
                existing_workouts = Workout.objects.filter(user=self.request.user)
                context = {
                    'form': self.form_class(None),
                    'existing_workouts': existing_workouts,
                    'name_error': True,
                }
                # Renders the template with the name error
                return render(request, self.template_name, context)

            workout.user = self.request.user
            # Finalize workout
            workout.save()
            # Gets the pk for the reverse url
            kwargs = {
                'pk': workout.id,
            }
            # Sends the user to the workout's detail page with the workout id
            # that was just created
            return HttpResponseRedirect(reverse('workout:workout_detail', kwargs=kwargs))

        else:
            existing_workouts = Workout.objects.filter(user=self.request.user)
            # Forms are returned with form validation errors
            context = {
                'form': form,
                'existing_workouts': existing_workouts,
                'name_error': False,
            }
            return render(request, self.template_name, context)

class WorkoutDetail(LoginRequiredMixin, generic.detail.DetailView):
    model = Workout
    template_name = 'workout/workout_detail.html'
    form_class = WorkoutCreationForm
    login_url = 'home:login'

    def total_volume(self, logs):
        '''Function to caluclate volume of all logs'''
        workout_volume = 0
        for log in logs:
            log_sets = Set.objects.filter(log=log)
            for set in log_sets:
                if set.unit == 'lbs':
                    workout_volume += set.weight*set.reps
                else:
                    workout_volume += set.weight*2.20462*set.reps
        return workout_volume

    def get_log_volume(self, log):
        '''Gets volume of a log'''
        log_volume = 0
        log_sets = Set.objects.filter(log=log)
        for set in log_sets:
            if set.unit == 'lbs':
                log_volume += set.weight*set.reps
            else:
                log_volume += set.weight*2.20462*set.reps
        return log_volume

    def get_chart_data(self, logs):
        '''Gets data for chart.js plot'''
        logs_ordered = logs.reverse()
        if len(logs_ordered) >= 5:
            graph_logs = logs_ordered[len(logs_ordered) - 5:]
        else:
            graph_logs = logs_ordered

        labels = []
        volumes = []
        for log in graph_logs:
            volumes.append(self.get_log_volume(log))
            labels.append(log.created_at)

        return (volumes, labels)

    def get_object(self, queryset=None):
        '''Ensures the user owns the object'''
        obj = super(WorkoutDetail, self).get_object(queryset=queryset)
        if obj.user != self.request.user:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        '''Returns the context data for the workout'''
        context = super(WorkoutDetail, self).get_context_data(**kwargs)
        workout = self.get_object()
        context['exercises'] = Exercise.objects.filter(workout=workout)
        logs = Log.objects.filter(workout=workout, status='closed').order_by('-created_at')
        context['completed_workouts'] = logs.count()
        if len(logs) > 0:
            context['last_workout'] = logs[0]
        else:
            context['last_workout'] = None
        context['workout_volume'] = '{:,}'.format(self.total_volume(logs))
        context['chart_data'] = self.get_chart_data(logs)
        context['form'] = self.form_class(instance=workout)
        return context

class WorkoutEdit(LoginRequiredMixin, View):
    template_name = 'workout/workout_edit.html'
    form_class = WorkoutCreationForm
    login_url = 'home:login'

    def post(self, request, pk):
        existing_workout = get_object_or_404(Workout, id=pk)
        if existing_workout.user == request.user:
            existing_workout_name = existing_workout.workout_name
            form = self.form_class(self.request.POST, instance=existing_workout)
            if form.is_valid():
                workout = form.save(commit=False)
                existing_workout_names = Workout.objects.filter(user=self.request.user).values_list('workout_name', flat=True)
                if form.cleaned_data['workout_name'] == existing_workout_name:
                    workout.save()
                    kwargs = {
                        'pk': pk,
                    }
                    return HttpResponseRedirect(reverse('workout:workout_detail', kwargs=kwargs))

                elif form.cleaned_data['workout_name'] not in existing_workout_names:
                    workout.save()
                    kwargs = {
                        'pk': pk,
                    }
                    return HttpResponseRedirect(reverse('workout:workout_detail', kwargs=kwargs))

                else:
                    context = {
                        'form': form,
                        'existing_workout_name': existing_workout_name,
                        'existing_workout_names': existing_workout_names,
                        'name_error': 'You cannot have two workouts with the same name!'
                    }
                    return render(request, self.template_name, context=context)
        else:
            raise Http404('This is not your workout.')

class WorkoutDelete(LoginRequiredMixin, generic.edit.DeleteView):
    '''Deletes the selected workout'''
    template_name = 'workout/workout_delete.html'
    success_url = reverse_lazy('home:index')

    def get_object(self):
        '''
        Defines what object to get on delete
        '''
        id_ = self.kwargs.get("pk")
        return get_object_or_404(Workout, id=id_)

    def post(self, request, pk):
        if 'cancel' in request.POST:
            kwargs = {
                'pk': pk,
            }
            return HttpResponseRedirect(reverse('workout:workout_detail', kwargs=kwargs))
        else:
            workout = get_object_or_404(Workout, id=pk)
            if workout.user == self.request.user:
                return super(WorkoutDelete, self).post(request)
            else:
                raise Http404('This is not your workout.')

class ExerciseDelete(LoginRequiredMixin, generic.edit.DeleteView):
    '''Deletes the selected workout'''
    template_name = 'workout/exercise_delete.html'
    login_url = "home:login"

    def get_object(self):
        '''
        Defines what object to get on delete
        '''
        id_ = self.kwargs.get("exercise_pk")
        return get_object_or_404(Exercise, id=id_)

    def get_success_url(self):
        pk = self.kwargs.get('pk')
        kwargs = {
            'pk': pk,
        }
        return reverse('workout:workout_detail', kwargs=kwargs)

    def post(self, request, pk, exercise_pk):
        if 'cancel' in request.POST:
            kwargs = {
                'pk': pk,
            }
            return HttpResponseRedirect(reverse('workout:workout_detail', kwargs=kwargs))

        else:
            exercise = get_object_or_404(Exercise, id=exercise_pk)
            if exercise.user == self.request.user:
                return super(ExerciseDelete, self).post(request)
            else:
                raise Http404('This is not your exercise.')

class ExerciseCreate(LoginRequiredMixin, View):
    template_name = 'workout/exercise_create.html'
    login_url = 'home:login'
    form_class = ExerciseForm

    def get(self, request, pk):
        workout = get_object_or_404(Workout, id=pk)

        if workout.user == self.request.user:
            exercises = ExerciseByGroup.objects.all()
            exercise_dict = {
                'Chest': exercises.filter(type='CHEST'),
                'Back': exercises.filter(type='BACK'),
                'Shoulders': exercises.filter(type='SHOULDERS'),
                'Arms': exercises.filter(type='ARMS'),
                'Abs': exercises.filter(type='ABS'),
                'Legs': exercises.filter(type='LEGS'),
            }
            context = {
                'workout': workout,
                'exercise_dict': exercise_dict,
            }
            return render(request, self.template_name, context)

        else:
            raise Http404('This is not your workout')

    def post(self, request, pk):
        workout = get_object_or_404(Workout, id=pk)
        if workout.user == self.request.user:
            exercises = ExerciseByGroup.objects.all()

            for exercise in exercises:
                try:
                    exercise_status = request.POST[str(exercise.id)]
                    if exercise_status == 'on':
                        new_exercise = Exercise.objects.create(user=request.user, workout=workout, exercise=exercise)
                        new_exercise.save()
                except:
                    # Does nothing if the key is not present in the POST
                    pass
            kwargs = {
                'pk': pk,
            }
            return HttpResponseRedirect(reverse('workout:workout_detail', kwargs=kwargs))

        else:
            raise Http404('This is not your workout.')

# ------------------------------------------------------------------------------
