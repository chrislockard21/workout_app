from workout.models import Workout, Exercise, ExerciseByGroup
from log.models import Log, Set, SetHistory, LogHistory
from django.db.models import Count
from django.shortcuts import get_object_or_404

class Statistics():
    '''Object to capture user statistics'''

    def __init__(self, request):
        '''Initializes the statistics object with all relavent user data
        to save some queries'''
        self.user = request.user
        self.workouts = Workout.objects.filter(user=self.user)
        self.logs = Log.objects.filter(workout__in=self.workouts, status='open')
        self.log_history = LogHistory.objects.filter(user=self.user)
        self.set_history = SetHistory.objects.filter(user=self.user)
        self.sets = Set.objects.filter(user=self.user)
        self.exercises = Exercise.objects.filter(user=request.user)

    def log_widget(self):
        '''Gets the data for the log widgets'''
        return {
            log:(
                self.sets.filter(log=log).count(),
                self.exercises.filter(workout=log.workout).count()
            ) for log in self.logs
        }

    def total_volume(self):
        '''Gets the users total volume (will convert kg to lbs)'''
        volume = 0
        for log in self.log_history:
            sets = self.set_history.filter(log_history=log)
            for set in sets:
                if set.unit == 'lbs':
                    volume += set.weight*set.reps
                else:
                    # Convert kg to lbs
                    volume += set.weight*2.20462*set.reps
        return '{:,}'.format(round(volume, 2))

    def max_exercise(self):
        '''Gets the most used exercise by the user'''
        exercise_counts = self.exercises.values('exercise').annotate(freq=Count('exercise'))
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
        return {workout:self.exercises.filter(workout=workout) for workout in self.workouts}

    def log_count(self):
        '''Gets the total log history count'''
        return self.log_history.count

    def open_log_count(self):
        '''Gets the total open log count'''
        return self.logs.count

    def exercise_use_rate(self, exercise):
        return (Exercise.objects.filter(user=self.user, exercise=exercise).count)
