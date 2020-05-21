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

    def get(self, request):
        '''Creates the GET method for the create view. This method will only
        be used for errors on the index modal'''
        # Instantiate the class form and formsets to be passed to the template
        existing_workouts = Workout.objects.filter(user=self.request.user)
        context = {
            'form': self.form_class(None),
            'existing_workouts': existing_workouts,
            'name_error': False,
        }
        # Renders the workout creation template with the above context
        return render(request, self.template_name, context)

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

class WorkoutDetail(LoginRequiredMixin, View):
    '''
    Renders the detail page for a workout

    Set, log, or workout if non-existent are returned in empty lists. Some of
    the django query methods will error if the objects do not exist.
    '''
    template_name = 'workout/workout_detail.html'
    login_url = 'home:login'
    form_class = WorkoutCreationForm

    def get(self, request, pk):
        '''Creates the GET method for the detail view'''
        workout = Workout.objects.get(id=pk)
        if workout.user == self.request.user:
            # Initializes the workout info object
            workout_info = WorkoutInfo(request, pk)
            # Creates the form with the info from workout
            form = self.form_class(instance=workout)
            # Gets the logs for graphing
            graph_logs = workout_info.get_graph_logs()

            # Gets the total volume for the workout
            workout_volume = 0
            for log in workout_info.logs:
                workout_volume += log_volume(log)

            # Unpacks data for chart.js
            labels = []
            volumes = []
            for log in graph_logs:
                volumes.append(log_volume(log))
                labels.append(log.created_at)

            context = {
                'workout': workout,
                'workout_exercises': workout_info.get_workout_exercises(),
                'total_logs_count': workout_info.get_log_count(),
                'last_workout': workout_info.get_latest_log(),
                'workout_existing_name': workout_info.workout.workout_name,
                'workout_existing_desc': workout_info.workout.workout_desc,
                'workout_volume': workout_volume,
                'volumes': volumes,
                'labels': labels,
                'form': form,
                'name_error': False
            }
            return render(request, self.template_name, context)

        else:
            return Http404('This is not your workout.')

    def post(self, request, pk):
        workout_existing = Workout.objects.get(id=pk)
        if workout_existing.user == self.request.user:
            workout_existing_name = workout_existing.workout_name

            # Passes the form information into the workout form and exercise
            # formset for processing
            form = self.form_class(self.request.POST, instance=workout_existing)

            # Checks if the forms are valid
            if form.is_valid():
                workout = form.save(commit=False)
                # Gets existing workout names
                existing_workout_names = Workout.objects.filter(user=self.request.user).values_list('workout_name', flat=True)

                if form.cleaned_data['workout_name'] == workout_existing_name:
                    workout.save()
                    kwargs = {
                        'pk': pk,
                    }
                    return HttpResponseRedirect(reverse('workout:workout_detail', kwargs=kwargs))

                elif form.cleaned_data['workout_name'] in existing_workout_names:
                    workout = Workout.objects.get(id=pk)
                    if workout.user == self.request.user:
                        # Initializes the workout info object
                        workout_info = WorkoutInfo(request, pk)
                        # Creates the form with the info from workout
                        form = self.form_class(instance=workout)
                        # Gets the logs for graphing
                        graph_logs = workout_info.get_graph_logs()

                        # Gets the total volume for the workout
                        workout_volume = 0
                        for log in workout_info.logs:
                            workout_volume += log_volume(log)

                        # Unpacks data for chart.js
                        labels = []
                        volumes = []
                        for log in graph_logs:
                            volumes.append(log_volume(log))
                            labels.append(log.created_at)

                    context = {
                        'workout': workout,
                        'workout_exercises': workout_info.get_workout_exercises(),
                        'total_logs_count': workout_info.get_log_count(),
                        'last_workout': workout_info.get_latest_log(),
                        'workout_existing_name': workout_info.workout.workout_name,
                        'workout_existing_desc': workout_info.workout.workout_desc,
                        'workout_volume': workout_volume,
                        'volumes': volumes,
                        'labels': labels,
                        'form': form,
                        'name_error': True
                    }
                    return render(request, self.template_name, context)

                else:
                    # Save workout since it has a unique name for the user
                    workout.save()
                    kwargs = {
                        'pk': pk,
                    }
                    return HttpResponseRedirect(reverse('workout:workout_detail', kwargs=kwargs))

            else:
                workout_exercises = Exercise.objects.filter(workout=workout_existing)
                context = {
                    'workout': workout_existing,
                    'workout_exercises': workout_exercises,
                    'form': form,
                    'name_error': False,
                }
                return render(request, self.template_name, context)

        else:
            return Http404('This is not your workout.')


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
                return Http404('This is not your workout.')

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
                return Http404('This is not your exercise.')

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
            return Http404('This is not your workout')

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
            return Http404('This is not your workout.')

# ------------------------------------------------------------------------------


# class WorkoutEdit(LoginRequiredMixin, View):
#     '''Renders the view that allows users to edit workouts/exercises'''
#     # Class attributes to store template information, login controls, forms,
#     # and variables
#     template_name = 'workout/workout_edit.html'
#     login_url = 'home:login'
#     form_class = WorkoutCreationForm
#
#     def get(self, request, pk):
#         '''
#         Creates the GET method for the edit view
#         '''
#         workout = Workout.objects.get(id=pk)
#         if workout.user == self.request.user:
#             workout_exercises = Exercise.objects.filter(workout=workout)
#             # Creates forms with associated objects
#             form = self.form_class(instance=workout)
#
#             context = {
#                 'workout': workout,
#                 'workout_exercises': workout_exercises,
#                 'form': form,
#                 'name_error': False,
#             }
#             return render(request, self.template_name, context)
#         else:
#             return Http404('This is not your workout.')
#
#
#
#     def post(self, request, pk):
#         '''Creates the POST method for the edit view'''
#         workout_existing = Workout.objects.get(id=pk)
#         if workout_existing.user == self.request.user:
#             workout_existing_name = workout_existing.workout_name
#
#             # Passes the form information into the workout form and exercise
#             # formset for processing
#             form = self.form_class(self.request.POST, instance=workout_existing)
#
#             # Checks if the forms are valid
#             if form.is_valid():
#                 workout = form.save(commit=False)
#                 # Gets existing workout names
#                 existing_workout_names = Workout.objects.filter(user=self.request.user).values_list('workout_name', flat=True)
#
#                 if form.cleaned_data['workout_name'] == workout_existing_name:
#                     workout.save()
#                     kwargs = {
#                         'pk': pk,
#                     }
#                     return HttpResponseRedirect(reverse('workout:workout_detail', kwargs=kwargs))
#
#                 elif form.cleaned_data['workout_name'] in existing_workout_names:
#                     workout_exercises = Exercise.objects.filter(workout=workout_existing)
#                     context = {
#                         'workout': workout_existing,
#                         'workout_exercises': workout_exercises,
#                         'form': form,
#                         'name_error': True,
#                     }
#                     return render(request, self.template_name, context)
#
#                 else:
#                     # Save workout since it has a unique name for the user
#                     workout.save()
#                     kwargs = {
#                         'pk': pk,
#                     }
#                     return HttpResponseRedirect(reverse('workout:workout_detail', kwargs=kwargs))
#
#             else:
#                 workout_exercises = Exercise.objects.filter(workout=workout_existing)
#                 context = {
#                     'workout': workout_existing,
#                     'workout_exercises': workout_exercises,
#                     'form': form,
#                     'name_error': False,
#                 }
#                 return render(request, self.template_name, context)
#
#         else:
#             return Http404('This is not your workout.')
